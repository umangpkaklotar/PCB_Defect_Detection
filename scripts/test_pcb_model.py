# ============================================================
# PCB DEFECT DETECTION - TEST TRAINED MODEL
# ============================================================
#
# PURPOSE:
# Colab ma train thayela best.pt model ne VS Code ma load kari
# ek PCB image par defect detection karvu.
# ============================================================

from ultralytics import YOLO


# ------------------------------------------------------------
# 1. Trained model load karo
# ------------------------------------------------------------

model = YOLO(
    r"D:\smart-manufacturing-ai\models\pcb_yolov8n_v1\weights\best.pt"
)


# ------------------------------------------------------------
# 2. PCB image par prediction karo
# ------------------------------------------------------------
#
# source = tamari test PCB image no path
# conf = minimum confidence threshold
# save = output image save karse
# ------------------------------------------------------------

results = model.predict(
    source=r"D:\smart-manufacturing-ai\uploads\images\test_pcb.jpg",
    conf=0.25,
    save=True
)


# ------------------------------------------------------------
# 3. Detection complete
# ------------------------------------------------------------

print("\n======================================")
print("PCB DEFECT DETECTION COMPLETED")
print("======================================")