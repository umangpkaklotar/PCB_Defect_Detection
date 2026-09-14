# ============================================================
# PCB DEFECT DETECTION - VIDEO
# ============================================================
#
# PURPOSE:
# Trained YOLO model ne video par run kari ne
# PCB defects detect karva.
#
# Input:
#     pcb_test_video.mp4
#
# Model:
#     best.pt
#
# Output:
#     pcb_detected_video.mp4
# ============================================================

from ultralytics import YOLO
import os


# ------------------------------------------------------------
# 1. TRAINED YOLO MODEL LOAD KARO
# ------------------------------------------------------------

MODEL_PATH = r"D:\smart-manufacturing-ai\models\pcb_yolov8n_v1\weights\best.pt"

model = YOLO(MODEL_PATH)


# ------------------------------------------------------------
# 2. INPUT VIDEO
# ------------------------------------------------------------

INPUT_VIDEO = r"D:\smart-manufacturing-ai\uploads\videos\pcb_test_video.mp4"


# ------------------------------------------------------------
# 3. OUTPUT FOLDER
# ------------------------------------------------------------

OUTPUT_FOLDER = r"D:\smart-manufacturing-ai\uploads\videos\detected"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# 4. VIDEO PAR YOLO PREDICTION
# ------------------------------------------------------------

results = model.predict(
    source=INPUT_VIDEO,

    # Detection confidence
    conf=0.25,

    # Output video save karvu
    save=True,

    # Output folder
    project=OUTPUT_FOLDER,

    # Output experiment name
    name="pcb_video_detection",

    # Existing folder hoy to error na ave
    exist_ok=True,

    # Detection video ma labels show karva
    show_labels=True,

    # Confidence score show karva
    show_conf=True
)


# ------------------------------------------------------------
# 5. COMPLETION MESSAGE
# ------------------------------------------------------------

print("\n======================================")
print("PCB VIDEO DETECTION COMPLETED")
print("======================================")

print("\nInput video:")
print(INPUT_VIDEO)

print("\nOutput folder:")
print(
    os.path.join(
        OUTPUT_FOLDER,
        "pcb_video_detection"
    )
)