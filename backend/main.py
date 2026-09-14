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

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ultralytics import YOLO

from PIL import Image
import io
import base64
import cv2
import numpy as np


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

    defect_counts = {}


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

        "detections": detections,

        "image": image_base64
    }


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
    file: UploadFile = File(...)
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
    file: UploadFile = File(...)
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