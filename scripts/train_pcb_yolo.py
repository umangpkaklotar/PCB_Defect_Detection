# ============================================================
# PCB DEFECT DETECTION - YOLOv8 TRAINING
# ============================================================
#
# PURPOSE:
# Train a YOLOv8 object detection model to detect 6 types
# of PCB defects.
#
# Classes:
#   0 -> copper
#   1 -> mousebite
#   2 -> open
#   3 -> pin-hole
#   4 -> short
#   5 -> spur
#
# Dataset:
# Roboflow-generated YOLO dataset
#
# Hardware:
# Current environment is CPU-only.
# ============================================================


# ------------------------------------------------------------
# 1. Import YOLO
# ------------------------------------------------------------

from ultralytics import YOLO


# ------------------------------------------------------------
# 2. Dataset configuration
# ------------------------------------------------------------
#
# data.yaml tells YOLO:
# - where training images are
# - where validation images are
# - where test images are
# - what the class names are
# ------------------------------------------------------------

DATA_YAML = r"D:\smart-manufacturing-ai\dataset\PCB_YOLO_Roboflow\data.yaml"


# ------------------------------------------------------------
# 3. Load pretrained YOLOv8 Nano model
# ------------------------------------------------------------
#
# yolov8n.pt = pretrained YOLOv8 Nano model.
#
# We use pretrained weights instead of training from zero.
# This is called Transfer Learning.
# ------------------------------------------------------------

model = YOLO("yolov8n.pt")


# ------------------------------------------------------------
# 4. Start training
# ------------------------------------------------------------
#
# epochs = number of times model sees the training dataset
#
# imgsz = image size used during training
#
# batch = number of images processed together
#
# device = "cpu" because current PyTorch has no CUDA
#
# project = where training results will be stored
#
# name = experiment name
# ------------------------------------------------------------

results = model.train(
    data=DATA_YAML,

    epochs=30,

    imgsz=512,

    batch=8,

    device="cpu",

    workers=2,

    project=r"D:\smart-manufacturing-ai\models",

    name="pcb_yolov8n_v1",

    pretrained=True,

    patience=10,

    plots=True,

    verbose=True
)


# ------------------------------------------------------------
# 5. Training completed
# ------------------------------------------------------------

print("\n======================================")
print("PCB YOLO TRAINING COMPLETED")
print("======================================")

print("\nBest model should be saved at:")

print(
    r"D:\smart-manufacturing-ai\models"
    r"\pcb_yolov8n_v1\weights\best.pt"
)