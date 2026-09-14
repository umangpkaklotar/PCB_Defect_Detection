# ============================================================
# SYNTHETIC PCB DEFECT GENERATOR
# ============================================================
#
# PURPOSE:
# Clean PCB image mathi controlled synthetic defect images
# create karvi.
#
# Aa images model testing / pipeline testing mate che.
#
# Generated defects:
#
# 1. open
# 2. short
# 3. mousebite
# 4. spur
# 5. copper
# 6. pin-hole
#
# IMPORTANT:
# Aa REAL manufacturing defects ni perfect simulation nathi.
# Aa controlled testing mate che.
# ============================================================


# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------

import cv2
import os
import numpy as np


# ------------------------------------------------------------
# INPUT IMAGE
# ------------------------------------------------------------
# Ahiya clean PCB image no path aapvo.
#
# Recommended:
# DeepPCB nu *_temp.jpg image use karo.
#
# Example:
#
# D:\smart-manufacturing-ai\dataset\DeepPCB-master\
# PCBData\group00041\00041\00041000_temp.jpg
# ------------------------------------------------------------

INPUT_IMAGE = (
    r"D:\smart-manufacturing-ai\dataset\DeepPCB-master"
    r"\PCBData\group00041\00041\00041000_temp.jpg"
)


# ------------------------------------------------------------
# OUTPUT FOLDER
# ------------------------------------------------------------
# Generated synthetic images aa folder ma save thashe.
# ------------------------------------------------------------

OUTPUT_FOLDER = (
    r"D:\smart-manufacturing-ai"
    r"\dataset\synthetic_pcb"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ------------------------------------------------------------
# READ CLEAN PCB
# ------------------------------------------------------------

image = cv2.imread(INPUT_IMAGE)


if image is None:

    print("ERROR: PCB image read thai nathi.")

    print("Input path check karo:")

    print(INPUT_IMAGE)

    exit()


# ------------------------------------------------------------
# IMAGE SIZE
# ------------------------------------------------------------

height, width = image.shape[:2]


print("\n======================================")
print("SYNTHETIC PCB DEFECT GENERATOR")
print("======================================")

print("\nInput image:")
print(INPUT_IMAGE)

print("\nImage size:")
print(width, "x", height)


# ============================================================
# 1. OPEN DEFECT
# ============================================================
#
# PURPOSE:
# PCB trace ni ek jagya remove kari ne artificial
# open-circuit jevu visual defect banavvu.
# ============================================================

open_img = image.copy()


# Central horizontal area select kariye.

y = height // 2
x = width // 2


# Small rectangular area erase kariye.

cv2.rectangle(
    open_img,
    (x - 35, y - 5),
    (x + 35, y + 5),
    (255, 255, 255),
    -1
)


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_open.jpg"
    ),
    open_img
)


# ============================================================
# 2. SHORT DEFECT
# ============================================================
#
# PURPOSE:
# Be nearby regions vachche artificial bridge draw kari
# short-circuit jevu visual defect create karvu.
# ============================================================

short_img = image.copy()


# Two nearby points define kariye.

p1 = (
    width // 2 - 50,
    height // 2
)

p2 = (
    width // 2 + 50,
    height // 2
)


# Artificial connection draw kariye.

cv2.line(
    short_img,
    p1,
    p2,
    (0, 0, 0),
    8
)


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_short.jpg"
    ),
    short_img
)


# ============================================================
# 3. MOUSEBITE DEFECT
# ============================================================
#
# PURPOSE:
# PCB edge par small circular notches create karva.
# ============================================================

mousebite_img = image.copy()


edge_y = height // 2


for offset in [-30, 0, 30]:

    center = (
        10,
        edge_y + offset
    )

    cv2.circle(
        mousebite_img,
        center,
        12,
        (255, 255, 255),
        -1
    )


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_mousebite.jpg"
    ),
    mousebite_img
)


# ============================================================
# 4. SPUR DEFECT
# ============================================================
#
# PURPOSE:
# Existing trace mathi unwanted branch/protrusion jevu
# artificial structure create karvu.
# ============================================================

spur_img = image.copy()


spur_start = (
    width // 2,
    height // 2
)

spur_end = (
    width // 2 + 50,
    height // 2 - 50
)


cv2.line(
    spur_img,
    spur_start,
    spur_end,
    (0, 0, 0),
    7
)


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_spur.jpg"
    ),
    spur_img
)


# ============================================================
# 5. COPPER DEFECT
# ============================================================
#
# PURPOSE:
# PCB par unwanted copper-like extra region create karvu.
# ============================================================

copper_img = image.copy()


cx = width // 2
cy = height // 2


cv2.rectangle(
    copper_img,
    (cx - 20, cy - 20),
    (cx + 25, cy + 25),
    (0, 0, 0),
    -1
)


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_copper.jpg"
    ),
    copper_img
)


# ============================================================
# 6. PIN-HOLE DEFECT
# ============================================================
#
# PURPOSE:
# Surface par tiny hole jevo artificial defect create karvu.
# ============================================================

pinhole_img = image.copy()


cv2.circle(
    pinhole_img,
    (
        width // 2,
        height // 2
    ),
    5,
    (255, 255, 255),
    -1
)


cv2.imwrite(
    os.path.join(
        OUTPUT_FOLDER,
        "synthetic_pin-hole.jpg"
    ),
    pinhole_img
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n======================================")
print("SYNTHETIC DEFECT IMAGES CREATED")
print("======================================")

print("\nOutput folder:")

print(OUTPUT_FOLDER)

print("\nCreated images:")

print("1. synthetic_open.jpg")

print("2. synthetic_short.jpg")

print("3. synthetic_mousebite.jpg")

print("4. synthetic_spur.jpg")

print("5. synthetic_copper.jpg")

print("6. synthetic_pin-hole.jpg")

print("\n======================================")