# ============================================================
# SYNTHETIC PCB DEFECT TEST
# ============================================================
#
# PURPOSE:
# Synthetic defect images ne trained YOLO model sathe test
# karva.
#
# Aapde 6 images test karishu:
#
# 1. open
# 2. short
# 3. mousebite
# 4. spur
# 5. copper
# 6. pin-hole
#
# IMPORTANT:
# Aa synthetic images manually create karel che.
# Aa REAL test-set accuracy nathi.
# Aa controlled experiment che.
# ============================================================


# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------

from ultralytics import YOLO
import os


# ------------------------------------------------------------
# MODEL PATH
# ------------------------------------------------------------
# Aapdu trained YOLO model.
# ------------------------------------------------------------

MODEL_PATH = (
    r"D:\smart-manufacturing-ai"
    r"\models\pcb_yolov8n_v1"
    r"\weights\best.pt"
)


# ------------------------------------------------------------
# SYNTHETIC IMAGE FOLDER
# ------------------------------------------------------------
# Pela create karel 6 images aa folder ma che.
# ------------------------------------------------------------

IMAGE_FOLDER = (
    r"D:\smart-manufacturing-ai"
    r"\dataset\synthetic_pcb"
)


# ------------------------------------------------------------
# CONFIDENCE
# ------------------------------------------------------------
# Pela 0.50 thi test kariye.
# ------------------------------------------------------------

CONFIDENCE = 0.50


# ------------------------------------------------------------
# EXPECTED DEFECT
# ------------------------------------------------------------
# Darek image ma aapde kaya defect create karyo che
# te ahiya define kariye.
# ------------------------------------------------------------

TEST_IMAGES = {

    "synthetic_open.jpg": "open",

    "synthetic_short.jpg": "short",

    "synthetic_mousebite.jpg": "mousebite",

    "synthetic_spur.jpg": "spur",

    "synthetic_copper.jpg": "copper",

    "synthetic_pin-hole.jpg": "pin-hole"

}


# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

print("\nLoading trained YOLO model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# HEADER
# ============================================================

print("\n==============================================")

print("SYNTHETIC PCB DEFECT TEST")

print("==============================================")


print("\nConfidence:", CONFIDENCE)

print("\n")


# ------------------------------------------------------------
# RESULT COUNTERS
# ------------------------------------------------------------

correct = 0

wrong = 0


# ============================================================
# TEST EACH IMAGE
# ============================================================

for image_name, expected_defect in TEST_IMAGES.items():


    # --------------------------------------------------------
    # IMAGE PATH
    # --------------------------------------------------------

    image_path = os.path.join(
        IMAGE_FOLDER,
        image_name
    )


    print("\n----------------------------------------------")

    print("Image:", image_name)

    print("Expected:", expected_defect)

    print("----------------------------------------------")


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not os.path.exists(image_path):

        print("ERROR: Image not found.")

        print(image_path)

        wrong += 1

        continue


    # --------------------------------------------------------
    # YOLO PREDICTION
    # --------------------------------------------------------

    results = model.predict(
        source=image_path,
        conf=CONFIDENCE,
        imgsz=512,
        verbose=False
    )


    result = results[0]


    # --------------------------------------------------------
    # GET DETECTIONS
    # --------------------------------------------------------

    boxes = result.boxes


    # --------------------------------------------------------
    # STORE PREDICTED CLASSES
    # --------------------------------------------------------

    predictions = []


    for box in boxes:

        class_id = int(box.cls[0])

        confidence = float(box.conf[0])

        class_name = model.names[class_id]


        predictions.append(
            (
                class_name,
                confidence
            )
        )


    # --------------------------------------------------------
    # PRINT PREDICTIONS
    # --------------------------------------------------------

    if len(predictions) == 0:

        print("Predicted: No defect")


    else:

        for class_name, confidence in predictions:

            print(
                f"Predicted: "
                f"{class_name} "
                f"({confidence:.2f})"
            )


    # --------------------------------------------------------
    # CHECK WHETHER EXPECTED CLASS WAS FOUND
    # --------------------------------------------------------

    expected_found = False


    for class_name, confidence in predictions:

        if class_name == expected_defect:

            expected_found = True

            break


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if expected_found:

        print("Result: ✅ CORRECT")

        correct += 1

    else:

        print("Result: ❌ WRONG")

        wrong += 1


# ============================================================
# FINAL SUMMARY
# ============================================================

total_tests = correct + wrong


print("\n\n==============================================")

print("FINAL SYNTHETIC TEST RESULT")

print("==============================================")


print("\nTotal tests:", total_tests)

print("Correct:", correct)

print("Wrong:", wrong)


# ------------------------------------------------------------
# SIMPLE TEST ACCURACY
# ------------------------------------------------------------
# Aa synthetic test mate simple percentage calculate kariye.
# ------------------------------------------------------------

if total_tests > 0:

    accuracy = (
        correct / total_tests
    ) * 100

else:

    accuracy = 0


print(
    f"\nSynthetic Test Accuracy: "
    f"{accuracy:.2f}%"
)


print("\n==============================================")

print("IMPORTANT")

print("==============================================")

print(
    "Aa REAL MODEL ACCURACY nathi."
)

print(
    "Aa controlled synthetic test che."
)

print(
    "Final model evaluation actual labeled "
    "DeepPCB/Roboflow test set par karvi."
)

print("\n==============================================")