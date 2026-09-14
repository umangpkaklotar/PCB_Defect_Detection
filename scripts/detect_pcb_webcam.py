# ============================================================
# PCB INSPECTION SYSTEM
# WEBCAM + IMAGE UPLOAD + CONFIDENCE COMPARISON
# ============================================================
#
# PURPOSE:
# Aa program trained YOLO model thi PCB inspection kare che.
#
# INPUT MODES:
#
# 1. Webcam
# 2. PCB Image Upload
#
# IMAGE MODE MA:
# Same image ne 3 confidence thresholds par test karse:
#
#     0.25
#     0.50
#     0.70
#
# Aa thi aapde compare kari shakishu ke
# confidence threshold badlavathi detection kem change thay che.
#
# WEBCAM CONTROLS:
#
# I -> Image Upload
# Q -> Exit
#
# IMAGE MODE CONTROLS:
#
# W -> Webcam
# I -> Another Image
# Q -> Exit
# ============================================================


# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------
# cv2:
# Webcam, image reading ane image display mate.
#
# tkinter:
# Windows file picker open karva mate.
#
# os:
# Folder/file path handle karva mate.
#
# YOLO:
# Trained PCB defect detection model mate.
# ------------------------------------------------------------

import cv2
import os
import tkinter as tk

from tkinter import filedialog
from ultralytics import YOLO


# ------------------------------------------------------------
# MODEL PATH
# ------------------------------------------------------------
# Aa aapdu Colab ma train thayelu best.pt model che.
# ------------------------------------------------------------

MODEL_PATH = (
    r"D:\smart-manufacturing-ai"
    r"\models\pcb_yolov8n_v1"
    r"\weights\best.pt"
)


# ------------------------------------------------------------
# OUTPUT FOLDER
# ------------------------------------------------------------
# Different confidence results ni images aa folder ma save thashe.
# ------------------------------------------------------------

OUTPUT_FOLDER = (
    r"D:\smart-manufacturing-ai\runs\threshold_comparison"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# CONFIDENCE THRESHOLDS
# ------------------------------------------------------------
# Same PCB image ne aa 3 confidence par test karishu.
#
# 0.25 = 25%
# 0.50 = 50%
# 0.70 = 70%
# ------------------------------------------------------------

CONFIDENCE_LEVELS = [0.25, 0.50, 0.70]


# ------------------------------------------------------------
# LOAD TRAINED MODEL
# ------------------------------------------------------------
# best.pt memory ma load thashe.
# ------------------------------------------------------------

print("\nLoading PCB YOLO model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# FUNCTION 1
# IMAGE FILE SELECT KARVA MATE
# ============================================================
#
# PURPOSE:
# Windows file picker open kari ne user pase thi
# PCB image select karavvi.
# ============================================================

def select_image():

    root = tk.Tk()

    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select PCB Image",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png"),
            ("JPG Files", "*.jpg"),
            ("JPEG Files", "*.jpeg"),
            ("PNG Files", "*.png")
        ]
    )

    root.destroy()

    return file_path


# ============================================================
# FUNCTION 2
# DEFECT COUNT CALCULATE KARVA MATE
# ============================================================
#
# PURPOSE:
# YOLO result mathi darek defect ketli vaar detect thayo
# te count karvu.
#
# Example:
#
# copper    = 2
# open      = 1
# short     = 2
#
# ============================================================

def get_defect_counts(result):

    defect_counts = {}

    boxes = result.boxes

    for box in boxes:

        class_id = int(box.cls[0])

        class_name = model.names[class_id]

        if class_name not in defect_counts:

            defect_counts[class_name] = 0

        defect_counts[class_name] += 1

    return defect_counts


# ============================================================
# FUNCTION 3
# IMAGE PAR PASS / FAIL TEXT ADD KARVA MATE
# ============================================================
#
# PURPOSE:
# Detection image par inspection result display karvu.
#
# Rule:
#
# 0 defects -> PASS
# 1 or more defects -> FAIL
#
# NOTE:
# Aa currently demo rule che.
# Production ma acceptance criteria pachhi improve karishu.
# ============================================================

def add_result_text(image, total_defects, confidence):

    if total_defects > 0:

        result_text = (
            f"FAIL | Defects: {total_defects} "
            f"| Conf: {confidence:.2f}"
        )

        text_color = (0, 0, 255)

    else:

        result_text = (
            f"PASS | No Defects "
            f"| Conf: {confidence:.2f}"
        )

        text_color = (0, 255, 0)


    # --------------------------------------------------------
    # RESULT TEXT DRAW
    # --------------------------------------------------------

    cv2.rectangle(
        image,
        (10, 10),
        (600, 60),
        (255, 255, 255),
        -1
    )


    cv2.putText(
        image,
        result_text,
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        text_color,
        2
    )


    return image


# ============================================================
# FUNCTION 4
# SINGLE IMAGE PAR DETECTION
# ============================================================
#
# PURPOSE:
# Selected PCB image ne ek particular confidence threshold
# par detect karvu.
#
# Example:
#
# confidence = 0.50
#
# to only >= 50% confidence predictions display thashe.
# ============================================================

def run_image_detection(image_path, confidence):

    # --------------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------------

    image = cv2.imread(image_path)


    if image is None:

        print("\nERROR: Image read thai nathi.")

        return None, None, None


    # --------------------------------------------------------
    # YOLO PREDICTION
    # --------------------------------------------------------
    # Current PCB image par YOLO model run karishu.
    # --------------------------------------------------------

    results = model.predict(
        source=image,
        conf=confidence,
        imgsz=512,
        verbose=False
    )


    # --------------------------------------------------------
    # FIRST RESULT
    # --------------------------------------------------------

    result = results[0]


    # --------------------------------------------------------
    # DRAW BOUNDING BOXES
    # --------------------------------------------------------
    # YOLO automatically:
    #
    # Bounding box
    # Defect name
    # Confidence
    #
    # draw karse.
    # --------------------------------------------------------

    annotated_image = result.plot()


    # --------------------------------------------------------
    # TOTAL DEFECTS
    # --------------------------------------------------------

    total_defects = len(result.boxes)


    # --------------------------------------------------------
    # DEFECT COUNTS
    # --------------------------------------------------------

    defect_counts = get_defect_counts(result)


    # --------------------------------------------------------
    # PASS / FAIL TEXT
    # --------------------------------------------------------

    annotated_image = add_result_text(
        annotated_image,
        total_defects,
        confidence
    )


    return annotated_image, total_defects, defect_counts


# ============================================================
# FUNCTION 5
# IMAGE UPLOAD + 3 CONFIDENCE TEST
# ============================================================
#
# PURPOSE:
# User image select kare pachhi:
#
# 0.25
# 0.50
# 0.70
#
# badha confidence par model test karse.
# ============================================================

def image_mode():

    print("\n======================================")
    print("PCB IMAGE INSPECTION")
    print("======================================")


    # --------------------------------------------------------
    # SELECT IMAGE
    # --------------------------------------------------------

    image_path = select_image()


    # --------------------------------------------------------
    # USER E CANCEL KARYU
    # --------------------------------------------------------

    if image_path == "":

        print("\nNo image selected.")

        return "webcam"


    print("\nSelected image:")
    print(image_path)


    # --------------------------------------------------------
    # STORE RESULTS
    # --------------------------------------------------------

    all_results = []


    # ========================================================
    # RUN ALL CONFIDENCE LEVELS
    # ========================================================

    for confidence in CONFIDENCE_LEVELS:


        print("\n--------------------------------------")

        print(
            f"Testing Confidence: {confidence:.2f}"
        )

        print("--------------------------------------")


        # ----------------------------------------------------
        # RUN DETECTION
        # ----------------------------------------------------

        annotated_image, total_defects, defect_counts = (
            run_image_detection(
                image_path,
                confidence
            )
        )


        if annotated_image is None:

            continue


        # ----------------------------------------------------
        # PRINT TOTAL
        # ----------------------------------------------------

        print(
            f"Total defects: {total_defects}"
        )


        # ----------------------------------------------------
        # PRINT CLASS-WISE COUNT
        # ----------------------------------------------------

        print("\nDefect Details:")


        if len(defect_counts) == 0:

            print("No defects detected.")

        else:

            # ------------------------------------------------
            # Fixed order ma print karishu.
            # ------------------------------------------------

            defect_order = [
                "copper",
                "mousebite",
                "open",
                "pin-hole",
                "short",
                "spur"
            ]


            for defect in defect_order:

                count = defect_counts.get(
                    defect,
                    0
                )

                print(
                    f"{defect:10s}: {count}"
                )


        # ----------------------------------------------------
        # PASS / FAIL
        # ----------------------------------------------------

        if total_defects > 0:

            inspection_result = "FAIL"

        else:

            inspection_result = "PASS"


        print(
            f"\nInspection Result: "
            f"{inspection_result}"
        )


        # ----------------------------------------------------
        # SAVE RESULT IMAGE
        # ----------------------------------------------------
        # Example:
        #
        # result_conf_25.jpg
        # result_conf_50.jpg
        # result_conf_70.jpg
        # ----------------------------------------------------

        confidence_name = int(
            confidence * 100
        )


        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"result_conf_{confidence_name}.jpg"
        )


        cv2.imwrite(
            output_path,
            annotated_image
        )


        print(
            "\nSaved result:"
        )

        print(output_path)


        # ----------------------------------------------------
        # STORE RESULT FOR COMPARISON
        # ----------------------------------------------------

        all_results.append(
            (
                confidence,
                total_defects,
                defect_counts,
                annotated_image
            )
        )


    # ========================================================
    # SUMMARY TABLE
    # ========================================================

    print("\n\n======================================")
    print("CONFIDENCE COMPARISON")
    print("======================================")


    print(
        "\nConfidence       Total Defects"
    )

    print(
        "--------------------------------------"
    )


    for (
        confidence,
        total_defects,
        defect_counts,
        annotated_image
    ) in all_results:

        print(
            f"{confidence:.2f}"
            f"              "
            f"{total_defects}"
        )


    print(
        "======================================"
    )


    # ========================================================
    # SHOW EACH RESULT
    # ========================================================
    #
    # ENTER / SPACE:
    # Next confidence result
    #
    # W:
    # Webcam
    #
    # I:
    # Another image
    #
    # Q:
    # Exit
    # ========================================================

    for (
        confidence,
        total_defects,
        defect_counts,
        annotated_image
    ) in all_results:


        window_name = (
            f"PCB Inspection - "
            f"Confidence {confidence:.2f}"
        )


        cv2.imshow(
            window_name,
            annotated_image
        )


        print(
            f"\nShowing confidence "
            f"{confidence:.2f}"
        )

        print(
            "Press ENTER/SPACE for next result."
        )

        print(
            "Press W for Webcam."
        )

        print(
            "Press I for another image."
        )

        print(
            "Press Q to exit."
        )


        # ----------------------------------------------------
        # WAIT FOR KEY
        # ----------------------------------------------------

        while True:

            key = cv2.waitKey(0) & 0xFF


            # ENTER
            if key == 13:

                cv2.destroyWindow(
                    window_name
                )

                break


            # SPACE
            elif key == 32:

                cv2.destroyWindow(
                    window_name
                )

                break


            # W -> Webcam
            elif key == ord("w"):

                cv2.destroyAllWindows()

                return "webcam"


            # I -> Another Image
            elif key == ord("i"):

                cv2.destroyAllWindows()

                return "image"


            # Q -> Exit
            elif key == ord("q"):

                cv2.destroyAllWindows()

                return "quit"


    cv2.destroyAllWindows()


    # --------------------------------------------------------
    # After comparison, ask what to do.
    # --------------------------------------------------------

    print("\n======================================")
    print("IMAGE TEST COMPLETED")
    print("======================================")

    print("\nW -> Webcam")

    print("I -> Another Image")

    print("Q -> Exit")


    while True:

        key = cv2.waitKey(0) & 0xFF


        if key == ord("w"):

            return "webcam"


        elif key == ord("i"):

            return "image"


        elif key == ord("q"):

            return "quit"


# ============================================================
# FUNCTION 6
# WEBCAM MODE
# ============================================================
#
# PURPOSE:
# Live webcam frames par trained YOLO model run karvo.
#
# Webcam ma:
#
# I -> Image Upload
# Q -> Exit
# ============================================================

def webcam_mode():

    # --------------------------------------------------------
    # OPEN DEFAULT CAMERA
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)


    # --------------------------------------------------------
    # CHECK CAMERA
    # --------------------------------------------------------

    if not camera.isOpened():

        print("\nERROR: Webcam open thai nathi.")

        print(
            "Jo external webcam hoy to "
            "camera index 1 try karo."
        )

        return "quit"


    print("\n======================================")
    print("PCB LIVE WEBCAM MODE")
    print("======================================")

    print("\nPCB camera same mukvo.")

    print("\nControls:")

    print("I -> Image Upload")

    print("Q -> Exit")


    # ========================================================
    # LIVE LOOP
    # ========================================================

    while True:


        # ----------------------------------------------------
        # READ FRAME
        # ----------------------------------------------------

        ret, frame = camera.read()


        if not ret:

            print(
                "ERROR: Webcam frame read thai nathi."
            )

            break


        # ----------------------------------------------------
        # YOLO DETECTION
        # ----------------------------------------------------
        # Webcam ma currently 0.50 confidence use kariye.
        #
        # Aa value pachhi experiment pachhi change kari
        # shakishu.
        # ----------------------------------------------------

        webcam_confidence = 0.50


        results = model.predict(
            source=frame,
            conf=webcam_confidence,
            imgsz=512,
            verbose=False
        )


        # ----------------------------------------------------
        # GET RESULT
        # ----------------------------------------------------

        result = results[0]


        # ----------------------------------------------------
        # DRAW DETECTIONS
        # ----------------------------------------------------

        annotated_frame = result.plot()


        # ----------------------------------------------------
        # COUNT DEFECTS
        # ----------------------------------------------------

        total_defects = len(
            result.boxes
        )


        # ----------------------------------------------------
        # ADD PASS / FAIL
        # ----------------------------------------------------

        annotated_frame = add_result_text(
            annotated_frame,
            total_defects,
            webcam_confidence
        )


        # ----------------------------------------------------
        # DISPLAY WEBCAM
        # ----------------------------------------------------

        cv2.imshow(
            "PCB Inspection - Webcam",
            annotated_frame
        )


        # ----------------------------------------------------
        # KEYBOARD INPUT
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF


        # ----------------------------------------------------
        # I -> IMAGE UPLOAD
        # ----------------------------------------------------

        if key == ord("i"):

            camera.release()

            cv2.destroyAllWindows()

            return "image"


        # ----------------------------------------------------
        # Q -> EXIT
        # ----------------------------------------------------

        elif key == ord("q"):

            camera.release()

            cv2.destroyAllWindows()

            return "quit"


    # --------------------------------------------------------
    # RELEASE CAMERA
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    return "quit"


# ============================================================
# MAIN PROGRAM
# ============================================================
#
# Program webcam mode thi start thashe.
#
# Pachhi user:
#
# Webcam <-> Image Upload
#
# vachche switch kari shake.
# ============================================================


print("\n")
print("======================================")
print("PCB INSPECTION SYSTEM")
print("======================================")

print("\nStarting Webcam Mode...")


mode = "webcam"


while True:


    # --------------------------------------------------------
    # WEBCAM MODE
    # --------------------------------------------------------

    if mode == "webcam":

        mode = webcam_mode()


    # --------------------------------------------------------
    # IMAGE MODE
    # --------------------------------------------------------

    elif mode == "image":

        mode = image_mode()


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    elif mode == "quit":

        break


# ============================================================
# PROGRAM STOPPED
# ============================================================

print("\n======================================")

print("PCB INSPECTION SYSTEM STOPPED")

print("======================================")