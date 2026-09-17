"""MongoDB product and Product ID management for the PCB application."""

from datetime import datetime, timezone
from pathlib import Path
import os
from threading import Lock

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class ProductDatabaseError(Exception):
	"""Raised when MongoDB cannot complete a product operation."""


class ProductIdConflictError(ProductDatabaseError):
	"""Raised when a generated Product ID already exists."""


class ProductNotFoundError(ProductDatabaseError):
	"""Raised when an inspection references an unknown Product ID."""


_client = None
_database = None
_indexes_ready = False
_connection_lock = Lock()


def _get_database():
	"""Return the shared MongoDB database connection."""

	global _client, _database, _indexes_ready

	mongodb_uri = os.getenv("MONGODB_URI")
	database_name = os.getenv(
		"MONGODB_DATABASE",
		"smart_manufacturing_ai"
	)

	if not mongodb_uri:
		raise ProductDatabaseError(
			"MONGODB_URI is not configured in the .env file."
		)

	with _connection_lock:
		try:
			if _client is None:
				# Local development has low concurrency, so a small reusable
				# pool avoids opening a connection for every API request.
				_client = MongoClient(
					mongodb_uri,
					maxPoolSize=10,
					connectTimeoutMS=5000,
					serverSelectionTimeoutMS=5000,
					socketTimeoutMS=10000
				)

			_client.admin.command("ping")
			_database = _client[database_name]

			if not _indexes_ready:
				_database.products.create_index(
					[("product_id", ASCENDING)],
					unique=True,
					name="unique_product_id"
				)
				_database.products.create_index(
					[("created_at", DESCENDING)],
					name="recent_products"
				)
				_database.products.create_index(
					[("image_fingerprint", ASCENDING)],
					name="pcb_image_fingerprint"
				)
				_indexes_ready = True

			return _database

		except PyMongoError as error:
			raise ProductDatabaseError(
				f"MongoDB connection or setup failed: {error}"
			) from error


def initialize_database():
	"""Validate MongoDB access during application startup."""

	_get_database()


def close_database():
	"""Close the shared MongoDB client during application shutdown."""

	global _client, _database, _indexes_ready

	with _connection_lock:
		if _client is not None:
			_client.close()

		_client = None
		_database = None
		_indexes_ready = False


def create_product(product_type="PCB", image_fingerprint=None):
	"""Create a product using an atomic counter-backed Product ID."""

	database = _get_database()
	products = database.products
	counters = database.counters

	for attempt in range(3):
		try:
			counter = counters.find_one_and_update(
				{"_id": "product_id"},
				{"$inc": {"sequence_value": 1}},
				upsert=True,
				return_document=ReturnDocument.AFTER
			)

			product_id = f"PCB-{counter['sequence_value']:04d}"
			product = {
				"product_id": product_id,
				"product_type": product_type,
				"created_at": datetime.now(timezone.utc),
				"status": "PENDING",
				"inspection_count": 0,
				"inspection_history": []
			}

			if image_fingerprint:
				product["image_fingerprint"] = image_fingerprint

			products.insert_one(product)
			product.pop("_id", None)
			return product

		except DuplicateKeyError as error:
			# A legacy/manual record may occupy a generated number. The next
			# atomic counter value is retried rather than returning a duplicate.
			if attempt == 2:
				raise ProductIdConflictError(
					"Could not generate a unique Product ID."
				) from error

		except PyMongoError as error:
			raise ProductDatabaseError(
				f"Could not create product: {error}"
			) from error

	raise ProductIdConflictError(
		"Could not generate a unique Product ID."
	)


def get_product(product_id):
	"""Retrieve one product by its Product ID."""

	try:
		return _get_database().products.find_one(
			{"product_id": product_id},
			{"_id": 0}
		)
	except PyMongoError as error:
		raise ProductDatabaseError(
			f"Could not retrieve product: {error}"
		) from error


def list_recent_products(limit=20):
	"""Return the most recently created products."""

	try:
		products = _get_database().products.find(
			{},
			{"_id": 0}
		).sort("created_at", DESCENDING).limit(limit)
		return list(products)
	except PyMongoError as error:
		raise ProductDatabaseError(
			f"Could not list products: {error}"
		) from error


def find_product_by_fingerprint(image_fingerprint):
	"""Find a previously stored product with the same PCB image."""

	try:
		return _get_database().products.find_one(
			{"image_fingerprint": image_fingerprint},
			{"_id": 0}
		)
	except PyMongoError as error:
		raise ProductDatabaseError(
			f"Could not find PCB fingerprint: {error}"
		) from error


def record_inspection(product_id, inspection):
	"""Store the latest inspection summary against an existing product."""

	try:
		updated_product = _get_database().products.find_one_and_update(
			{"product_id": product_id},
			{
				"$set": {
					"image_fingerprint": inspection["image_fingerprint"],
					"status": inspection["status"],
					"last_inspection": {
						"inspected_at": datetime.now(timezone.utc),
						"status": inspection["status"],
						"total_defects": inspection["total_defects"],
						"highest_confidence": inspection[
							"highest_confidence"
						],
						"defect_counts": inspection["defect_counts"],
						"detections": inspection["detections"]
					}
				},
				"$inc": {
					"inspection_count": 1
				},
				"$push": {
					"inspection_history": {
						"inspected_at": datetime.now(timezone.utc),
						"status": inspection["status"],
						"total_defects": inspection["total_defects"],
						"highest_confidence": inspection[
							"highest_confidence"
						],
						"defect_counts": inspection["defect_counts"],
						"detections": inspection["detections"]
					}
				}
			},
			return_document=ReturnDocument.AFTER,
			projection={"_id": 0}
		)

		if updated_product is None:
			raise ProductNotFoundError(
				f"Product {product_id} was not found."
			)

		return updated_product

	except ProductNotFoundError:
		raise
	except PyMongoError as error:
		raise ProductDatabaseError(
		f"Could not record inspection: {error}"
	) from error
