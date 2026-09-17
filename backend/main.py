# ============================================================
# PCB AI QUALITY INSPECTION - FASTAPI BACKEND
# ============================================================
#
# PURPOSE:
# Frontend thi PCB image receive kari ne trained YOLO model
# thi defect detection karvu.
#
# FLOW:
#
# HTML/JS
#    ↓
# FastAPI
#    ↓
# best.pt
#    ↓
# YOLO
#    ↓
# Detection Result
#    ↓
# JSON
#    ↓
# Frontend
#
# ============================================================

from pathlib import Path
import hashlib

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ultralytics import YOLO

from PIL import Image
import io
import base64
import cv2
import numpy as np

from backend.product_manager import (
    ProductDatabaseError,
    ProductIdConflictError,
    ProductNotFoundError,
    close_database,
    create_product,
    get_product,
    find_product_by_fingerprint,
    initialize_database,
    list_recent_products,
    record_inspection,
)


PCB_DEFECT_CLASSES = (
    "open",
    "short",
    "mousebite",
    "spur",
    "copper",
    "pin-hole"
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PCB AI Quality Inspection API",
    description="YOLO based PCB defect detection API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================
#
# Frontend ane backend alag port par run thai shake.
# CORS frontend ne backend API access karva allow kare che.
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductCreateRequest(BaseModel):
    """Validated request body for creating a PCB product."""

    product_type: str = Field(
        default="PCB",
        min_length=1,
        max_length=100
    )


@app.on_event("startup")
def startup_database():
    """Check MongoDB without preventing inspection from loading."""

    try:
        initialize_database()
        print("MongoDB connected successfully.")
    except ProductDatabaseError as error:
        print(f"MongoDB unavailable: {error}")
        print("Product APIs will return errors until MongoDB is available.")


@app.on_event("shutdown")
def shutdown_database():
    close_database()


# ============================================================
# LOAD TRAINED YOLO MODEL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MODEL_PATH = PROJECT_ROOT / "models" / "pcb_yolov8n_v1" / "weights" / "best.pt"

print("Loading PCB YOLO model...")

model = YOLO(str(MODEL_PATH))

print("PCB YOLO model loaded successfully.")


# ============================================================
# HEALTH CHECK
# ============================================================
#
# Backend properly running che ke nahi te check karva.
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "message": "PCB AI Inspection API is running"
    }


# ============================================================
# PRODUCT APIs
# ============================================================

@app.post("/api/products", status_code=201)
def create_pcb_product(request: ProductCreateRequest):
    """Generate and store the next atomic PCB Product ID."""

    try:
        product_type = request.product_type.strip()
        if not product_type:
            raise HTTPException(
                status_code=422,
                detail="product_type cannot be empty."
            )

        product = create_product(product_type)
        return product
    except HTTPException:
        raise
    except ProductIdConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ProductDatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.get("/api/products/{product_id}")
def retrieve_pcb_product(product_id: str):
    """Retrieve a PCB product by Product ID."""

    if not product_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Product ID cannot be empty."
        )

    try:
        product = get_product(product_id.strip())
        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found."
            )
        return product
    except HTTPException:
        raise
    except ProductDatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.get("/api/products")
def recent_pcb_products(limit: int = 20):
    """List recently created PCB products."""

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 100."
        )

    try:
        return {
            "products": list_recent_products(limit)
        }
    except ProductDatabaseError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


# ============================================================
# IMAGE PREDICTION FUNCTION
# ============================================================
#
# Aa common function upload image ane camera frame banne
# mate YOLO prediction perform kare che.
# ============================================================

def run_prediction(image):

    # --------------------------------------------------------
    # YOLO prediction
    # --------------------------------------------------------

    results = model.predict(
        source=image,
        conf=0.50,
        imgsz=512,
        verbose=False
    )

    result = results[0]


    # --------------------------------------------------------
    # Detection data
    # --------------------------------------------------------

    detections = []

    defect_counts = {
        defect_class: 0
        for defect_class in PCB_DEFECT_CLASSES
    }


    # --------------------------------------------------------
    # Process every detected object
    # --------------------------------------------------------

    for box in result.boxes:

        class_id = int(box.cls[0])

        confidence = float(box.conf[0])

        class_name = model.names[class_id]


        # Bounding box coordinates
        x1, y1, x2, y2 = box.xyxy[0].tolist()


        detections.append({
            "class": class_name,
            "confidence": round(confidence, 4),
            "box": {
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2)
            }
        })


        # ----------------------------------------------------
        # Count defects
        # ----------------------------------------------------

        if class_name not in defect_counts:

            defect_counts[class_name] = 0

        defect_counts[class_name] += 1


    # --------------------------------------------------------
    # Total defects
    # --------------------------------------------------------

    total_defects = len(detections)


    # --------------------------------------------------------
    # Highest confidence
    # --------------------------------------------------------

    if detections:

        highest_confidence = max(
            item["confidence"]
            for item in detections
        )

    else:

        highest_confidence = 0


    # --------------------------------------------------------
    # PASS / FAIL
    # --------------------------------------------------------

    if total_defects > 0:

        status = "FAIL"

    else:

        status = "PASS"


    # --------------------------------------------------------
    # Create annotated image
    # --------------------------------------------------------

    annotated = result.plot()


    # OpenCV BGR → JPEG
    success, encoded_image = cv2.imencode(
        ".jpg",
        annotated
    )


    if not success:

        raise RuntimeError(
            "Could not encode annotated image."
        )


    # --------------------------------------------------------
    # Convert image to Base64
    # --------------------------------------------------------
    #
    # Frontend aa Base64 image ne directly display kari shake.
    # --------------------------------------------------------

    image_base64 = base64.b64encode(
        encoded_image.tobytes()
    ).decode("utf-8")


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "status": status,

        "total_defects": total_defects,

        "highest_confidence": round(
            highest_confidence,
            4
        ),

        "defect_counts": defect_counts,

        "defect_classes": list(PCB_DEFECT_CLASSES),

        "detections": detections,

        "image": image_base64
    }


def create_image_fingerprint(image):
    """Create a repeatable fingerprint from normalized PCB image pixels."""

    normalized = image.convert("RGB").resize((64, 64))
    return hashlib.sha256(normalized.tobytes()).hexdigest()


def link_inspection_to_product(
    result,
    image,
    product_id=None,
    create_new_on_change=True
):
    """Create, reuse, or update the product associated with an inspection."""

    image_fingerprint = create_image_fingerprint(image)
    existing_product = None
    product_reused = False

    if product_id:
        existing_product = get_product(product_id)
        if existing_product is None:
            raise ProductNotFoundError(
                f"Product {product_id} was not found."
            )

        stored_fingerprint = existing_product.get("image_fingerprint")
        if (
            create_new_on_change and
            stored_fingerprint and
            stored_fingerprint != image_fingerprint
        ):
            existing_product = find_product_by_fingerprint(
                image_fingerprint
            )
            if existing_product:
                product_id = existing_product["product_id"]
                product_reused = True
            else:
                product = create_product(
                    "PCB",
                    image_fingerprint=image_fingerprint
                )
                product_id = product["product_id"]
        else:
            product_reused = True
    else:
        existing_product = find_product_by_fingerprint(
            image_fingerprint
        )
        if existing_product:
            product_id = existing_product["product_id"]
            product_reused = True
        else:
            product = create_product(
                "PCB",
                image_fingerprint=image_fingerprint
            )
            product_id = product["product_id"]

    inspection = {
        **result,
        "image_fingerprint": image_fingerprint
    }
    record_inspection(product_id, inspection)
    result["product_id"] = product_id
    result["product_reused"] = product_reused
    result["product_message"] = (
        "Existing PCB found; details updated."
        if product_reused
        else "New PCB product record created."
    )
    return result


# ============================================================
# IMAGE UPLOAD API
# ============================================================
#
# Endpoint:
#
# POST /predict
#
# Frontend uploaded image aa endpoint par mokalse.
# ============================================================

@app.post("/predict")
async def predict_image(
    file: UploadFile = File(...),
    product_id: str | None = Form(default=None),
    new_product_on_change: bool = Form(default=True)
):

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    image_bytes = await file.read()


    # --------------------------------------------------------
    # Convert bytes → PIL Image
    # --------------------------------------------------------

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")


    # --------------------------------------------------------
    # YOLO prediction
    # --------------------------------------------------------

    result = run_prediction(image)

    try:
        return link_inspection_to_product(
            result,
            image,
            product_id,
            new_product_on_change
        )
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ProductIdConflictError as error:
        result["product_id"] = product_id
        result["database_warning"] = str(error)
        return result
    except ProductDatabaseError as error:
        result["product_id"] = product_id
        result["database_warning"] = str(error)
        return result


# ============================================================
# CAMERA FRAME API
# ============================================================
#
# Endpoint:
#
# POST /predict-frame
#
# JavaScript camera mathi frame capture kari ne aa endpoint
# par mokalse.
# ============================================================

@app.post("/predict-frame")
async def predict_frame(
    file: UploadFile = File(...),
    product_id: str | None = Form(default=None),
    new_product_on_change: bool = Form(default=False)
):

    # --------------------------------------------------------
    # Read frame
    # --------------------------------------------------------

    image_bytes = await file.read()


    # --------------------------------------------------------
    # Convert bytes → PIL Image
    # --------------------------------------------------------

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")


    # --------------------------------------------------------
    # YOLO prediction
    # --------------------------------------------------------

    result = run_prediction(image)

    try:
        return link_inspection_to_product(
            result,
            image,
            product_id,
            new_product_on_change
        )
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ProductIdConflictError as error:
        result["product_id"] = product_id
        result["database_warning"] = str(error)
        return result
    except ProductDatabaseError as error:
        result["product_id"] = product_id
        result["database_warning"] = str(error)
        return result


# ============================================================
# SERVE THE FRONTEND
# ============================================================
#
# Opening http://127.0.0.1:8000 now loads the web application and
# keeps the frontend and API on the same origin.
# ============================================================

@app.get("/", include_in_schema=False)
def frontend_home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)