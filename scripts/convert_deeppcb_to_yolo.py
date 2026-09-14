# ============================================================
# DeepPCB -> YOLO Dataset Converter
# ============================================================
#
# Aa script nu kaam:
#
# 1. DeepPCB dataset mathi *_test.jpg images shodhse
# 2. Ena corresponding .txt annotation files shodhse
# 3. DeepPCB annotation:
#
#       x1 y1 x2 y2 class_id
#
#    ne YOLO annotation:
#
#       class_id x_center y_center width height
#
#    ma convert karse.
#
# 4. Coordinates ne 0 thi 1 vachche normalize karse.
# 5. Images ane labels ne train / val / test ma divide karse.
# 6. data.yaml file banavse.
#
# IMPORTANT:
# Original DeepPCB dataset ne modify nahi kare.
# Original dataset safe rahe.
# ============================================================


# ------------------------------------------------------------
# 1. Required libraries import
# ------------------------------------------------------------

from pathlib import Path
import shutil
import random


# ------------------------------------------------------------
# 2. Dataset paths
# ------------------------------------------------------------

# Aapda original DeepPCB dataset nu location.
# Tamara computer ma aa exact path chhe.

SOURCE_DIR = Path(
    r"D:\smart-manufacturing-ai\dataset\DeepPCB-master\PCBData"
)


# ------------------------------------------------------------
# 3. Navo YOLO dataset kya banse?
# ------------------------------------------------------------

# Original dataset ni andar kai change nahi karvu.
# Navo converted dataset aa location par banse.

OUTPUT_DIR = Path(
    r"D:\smart-manufacturing-ai\dataset\PCB_YOLO"
)


# ------------------------------------------------------------
# 4. Dataset split ratio
# ------------------------------------------------------------

# 80% images -> training
# 10% images -> validation
# 10% images -> testing

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10


# ------------------------------------------------------------
# 5. Random seed
# ------------------------------------------------------------

# Same result repeat karva mate fixed random seed.

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ------------------------------------------------------------
# 6. YOLO class names
# ------------------------------------------------------------

# DeepPCB original class IDs:
#
# 1 -> open
# 2 -> short
# 3 -> mousebite
# 4 -> spur
# 5 -> copper
# 6 -> pin-hole
#
# YOLO class IDs 0 thi start thay chhe.
#
# Etle conversion:
#
# DeepPCB 1 -> YOLO 0 -> open
# DeepPCB 2 -> YOLO 1 -> short
# DeepPCB 3 -> YOLO 2 -> mousebite
# DeepPCB 4 -> YOLO 3 -> spur
# DeepPCB 5 -> YOLO 4 -> copper
# DeepPCB 6 -> YOLO 5 -> pin-hole

CLASS_MAPPING = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
}


CLASS_NAMES = [
    "open",
    "short",
    "mousebite",
    "spur",
    "copper",
    "pin-hole",
]


# ------------------------------------------------------------
# 7. Output folders create karo
# ------------------------------------------------------------

for split in ["train", "val", "test"]:

    (OUTPUT_DIR / "images" / split).mkdir(
        parents=True,
        exist_ok=True
    )

    (OUTPUT_DIR / "labels" / split).mkdir(
        parents=True,
        exist_ok=True
    )


# ------------------------------------------------------------
# 8. DeepPCB images find karva mate
# ------------------------------------------------------------

print("\nSearching for DeepPCB images...\n")


image_files = list(
    SOURCE_DIR.rglob("*_test.jpg")
)


print(
    f"Total *_test.jpg images found: {len(image_files)}"
)


# ------------------------------------------------------------
# 9. Check dataset
# ------------------------------------------------------------

if len(image_files) == 0:

    print("\nERROR: No *_test.jpg images found.")

    print(
        "\nPlease check this path:"
    )

    print(SOURCE_DIR)

    raise SystemExit


# ------------------------------------------------------------
# 10. Shuffle images
# ------------------------------------------------------------

random.shuffle(image_files)


# ------------------------------------------------------------
# 11. Calculate split sizes
# ------------------------------------------------------------

total_images = len(image_files)


train_count = int(
    total_images * TRAIN_RATIO
)


val_count = int(
    total_images * VAL_RATIO
)


test_count = total_images - train_count - val_count


# ------------------------------------------------------------
# 12. Split dataset
# ------------------------------------------------------------

train_images = image_files[
    :train_count
]


val_images = image_files[
    train_count:
    train_count + val_count
]


test_images = image_files[
    train_count + val_count:
]


print("\nDataset split:")
print("-------------------------")
print(f"Train : {len(train_images)}")
print(f"Val   : {len(val_images)}")
print(f"Test  : {len(test_images)}")
print("-------------------------\n")


# ------------------------------------------------------------
# 13. Function: convert one annotation file
# ------------------------------------------------------------

def convert_annotation(
    annotation_file,
    output_label_file,
    image_width=640,
    image_height=640
):

    """
    DeepPCB annotation ne YOLO annotation ma convert kare chhe.

    DeepPCB format:

        x1 y1 x2 y2 class_id

    YOLO format:

        class_id x_center y_center width height

    Badha coordinates normalize thay chhe.
    """

    yolo_lines = []


    # Annotation file read karo.

    with open(
        annotation_file,
        "r",
        encoding="utf-8"
    ) as file:

        lines = file.readlines()


    # Darek defect mate ek line.

    for line in lines:

        line = line.strip()


        # Empty line skip.

        if not line:
            continue


        # Space thi values alag karo.

        parts = line.split()


        # Expected:

        # x1 y1 x2 y2 class_id

        if len(parts) != 5:

            print(
                f"WARNING: Invalid annotation line: {line}"
            )

            continue


        x1 = float(parts[0])
        y1 = float(parts[1])
        x2 = float(parts[2])
        y2 = float(parts[3])

        original_class_id = int(parts[4])


        # ----------------------------------------------------
        # DeepPCB class ID -> YOLO class ID
        # ----------------------------------------------------

        if original_class_id not in CLASS_MAPPING:

            print(
                f"WARNING: Unknown class ID: "
                f"{original_class_id}"
            )

            continue


        yolo_class_id = CLASS_MAPPING[
            original_class_id
        ]


        # ----------------------------------------------------
        # Bounding box center
        # ----------------------------------------------------

        x_center = (
            (x1 + x2) / 2
        )

        y_center = (
            (y1 + y2) / 2
        )


        # ----------------------------------------------------
        # Bounding box width / height
        # ----------------------------------------------------

        box_width = (
            x2 - x1
        )

        box_height = (
            y2 - y1
        )


        # ----------------------------------------------------
        # Normalize coordinates
        # ----------------------------------------------------

        x_center /= image_width
        y_center /= image_height

        box_width /= image_width
        box_height /= image_height


        # ----------------------------------------------------
        # YOLO line
        # ----------------------------------------------------

        yolo_line = (
            f"{yolo_class_id} "
            f"{x_center:.6f} "
            f"{y_center:.6f} "
            f"{box_width:.6f} "
            f"{box_height:.6f}"
        )


        yolo_lines.append(
            yolo_line
        )


    # --------------------------------------------------------
    # Save YOLO annotation
    # --------------------------------------------------------

    with open(
        output_label_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(yolo_lines)
        )


# ------------------------------------------------------------
# 14. Function: process dataset split
# ------------------------------------------------------------

def process_split(
    image_list,
    split_name
):

    print(
        f"\nProcessing {split_name}..."
    )


    processed = 0
    skipped = 0


    for image_path in image_list:

        # ----------------------------------------------------
        # Example:
        #
        # 00041000_test.jpg
        #
        # becomes:
        #
        # 00041000.txt
        # ----------------------------------------------------

        image_name = image_path.stem

        # Remove "_test"

        base_name = image_name.replace(
            "_test",
            ""
        )


        # ----------------------------------------------------
        # Find corresponding annotation
        # ----------------------------------------------------

        annotation_path = None


        # Annotation file generally exists inside *_not folder.
        #
        # Example:
        #
        # group00041/
        #     00041/
        #         00041000_test.jpg
        #
        #     00041_not/
        #         00041000.txt

        parent_group = image_path.parent.parent


        possible_annotation = (
            parent_group
            / f"{parent_group.name}_not"
            / f"{base_name}.txt"
        )


        if possible_annotation.exists():

            annotation_path = (
                possible_annotation
            )

        else:

            # Backup search if folder structure differs.

            matches = list(
                SOURCE_DIR.rglob(
                    f"{base_name}.txt"
                )
            )


            if matches:

                annotation_path = matches[0]


        # ----------------------------------------------------
        # Annotation missing
        # ----------------------------------------------------

        if annotation_path is None:

            print(
                f"WARNING: Label not found for "
                f"{image_path.name}"
            )

            skipped += 1

            continue


        # ----------------------------------------------------
        # Destination paths
        # ----------------------------------------------------

        destination_image = (
            OUTPUT_DIR
            / "images"
            / split_name
            / image_path.name
        )


        destination_label = (
            OUTPUT_DIR
            / "labels"
            / split_name
            / f"{base_name}.txt"
        )


        # ----------------------------------------------------
        # Copy image
        # ----------------------------------------------------

        shutil.copy2(
            image_path,
            destination_image
        )


        # ----------------------------------------------------
        # Convert annotation
        # ----------------------------------------------------

        convert_annotation(
            annotation_path,
            destination_label
        )


        processed += 1


    print(
        f"{split_name} completed."
    )

    print(
        f"Processed: {processed}"
    )

    print(
        f"Skipped: {skipped}"
    )


# ------------------------------------------------------------
# 15. Process Train / Val / Test
# ------------------------------------------------------------

process_split(
    train_images,
    "train"
)


process_split(
    val_images,
    "val"
)


process_split(
    test_images,
    "test"
)


# ------------------------------------------------------------
# 16. Create data.yaml
# ------------------------------------------------------------

yaml_file = (
    OUTPUT_DIR / "data.yaml"
)


yaml_content = f"""path: {OUTPUT_DIR.as_posix()}

train: images/train
val: images/val
test: images/test

names:
  0: open
  1: short
  2: mousebite
  3: spur
  4: copper
  5: pin-hole
"""


with open(
    yaml_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        yaml_content
    )


# ------------------------------------------------------------
# 17. Final result
# ------------------------------------------------------------

print("\n======================================")
print("DeepPCB -> YOLO conversion completed!")
print("======================================")

print(
    f"\nYOLO dataset location:"
)

print(
    OUTPUT_DIR
)

print(
    f"\ndata.yaml created at:"
)

print(
    yaml_file
)

print("\nClasses:")

for index, name in enumerate(CLASS_NAMES):

    print(
        f"{index}: {name}"
    )

print("\nNext step:")
print(
    "Check PCB_YOLO/images and PCB_YOLO/labels folders."
)