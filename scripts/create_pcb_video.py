# ============================================================
# CREATE PCB TEST VIDEO FROM TEST IMAGES
# ============================================================
#
# PURPOSE:
# Roboflow na test images ne combine kari ne ek video banavvo.
#
# Aa video pachhi aapde trained YOLO model sathe test karishu.
# ============================================================

import cv2
import os
import glob

# ------------------------------------------------------------
# 1. TEST IMAGES NU FOLDER
# ------------------------------------------------------------
# Aa folder ma Roboflow na test images che.
# ------------------------------------------------------------

IMAGE_FOLDER = r"D:\smart-manufacturing-ai\dataset\PCB_YOLO_Roboflow\test\images"


# ------------------------------------------------------------
# 2. OUTPUT VIDEO NO PATH
# ------------------------------------------------------------

OUTPUT_VIDEO = r"D:\smart-manufacturing-ai\uploads\videos\pcb_test_video.mp4"


# ------------------------------------------------------------
# 3. BADHA JPG/PNG IMAGES FIND KARO
# ------------------------------------------------------------

image_files = []

image_files.extend(
    glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg"))
)

image_files.extend(
    glob.glob(os.path.join(IMAGE_FOLDER, "*.jpeg"))
)

image_files.extend(
    glob.glob(os.path.join(IMAGE_FOLDER, "*.png"))
)


# ------------------------------------------------------------
# 4. CHECK KARO KE IMAGES MALI KE NAHI
# ------------------------------------------------------------

if len(image_files) == 0:
    print("ERROR: Test images mali nathi.")
    print("Folder check karo:")
    print(IMAGE_FOLDER)
    exit()


print("Total test images found:", len(image_files))


# ------------------------------------------------------------
# 5. OUTPUT FOLDER CREATE KARO
# ------------------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_VIDEO),
    exist_ok=True
)


# ------------------------------------------------------------
# 6. FIRST IMAGE READ KARO
# ------------------------------------------------------------

first_image = cv2.imread(image_files[0])

if first_image is None:
    print("ERROR: First image read thai nathi.")
    exit()


height, width = first_image.shape[:2]


# ------------------------------------------------------------
# 7. VIDEO WRITER CREATE KARO
# ------------------------------------------------------------

fps = 10

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

video = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)


# ------------------------------------------------------------
# 8. BADHA IMAGES VIDEO MA ADD KARO
# ------------------------------------------------------------

for image_path in image_files[:20]:

    image = cv2.imread(image_path)

    if image is None:
        continue

    # Badha images same size ma rakho
    image = cv2.resize(
        image,
        (width, height)
    )

    # Ek image ne multiple frames sudhi show karo
    for _ in range(15):
        video.write(image)


# ------------------------------------------------------------
# 9. VIDEO SAVE KARO
# ------------------------------------------------------------

video.release()


print("\n======================================")
print("PCB TEST VIDEO CREATED")
print("======================================")

print("Video path:")
print(OUTPUT_VIDEO)