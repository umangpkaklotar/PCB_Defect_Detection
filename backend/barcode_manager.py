"""Generate and reuse barcode images for PCB Product IDs."""

from pathlib import Path
import re
from threading import Lock

import barcode
from barcode.writer import ImageWriter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BARCODE_DIRECTORY = PROJECT_ROOT / "qr_codes" / "barcodes"
_BARCODE_LOCK = Lock()
_SAFE_PRODUCT_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def get_or_create_barcode(product_id: str) -> Path:
    """Return the barcode image path, creating it once for this Product ID."""

    product_id = product_id.strip()
    if not product_id or not _SAFE_PRODUCT_ID.fullmatch(product_id):
        raise ValueError("Invalid Product ID for barcode generation.")

    barcode_path = BARCODE_DIRECTORY / f"{product_id}.png"

    with _BARCODE_LOCK:
        if barcode_path.exists():
            return barcode_path

        BARCODE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        code128 = barcode.get("code128", product_id, writer=ImageWriter())
        code128.save(
            str(barcode_path.with_suffix("")),
            options={"write_text": True}
        )

    return barcode_path
