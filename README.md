# PCB AI Quality Inspection & Smart Manufacturing

An end-to-end computer-vision project for detecting printed circuit board (PCB) defects with YOLOv8 and presenting inspection results through a FastAPI web application.

The current implementation supports:

- PCB image upload from the web dashboard
- YOLO-based defect detection
- Defect counts, confidence scores, and bounding boxes
- Automatic `PASS` / `FAIL` inspection status
- Base64-encoded annotated-image results
- Browser camera preview
- Offline image, video, webcam, dataset-conversion, evaluation, and synthetic-data scripts

MongoDB inspection history, QR/product tracking, predictive maintenance, Docker packaging, and cloud deployment are documented as future extensions. They are not implemented in the current repository.

## Table of contents

- [Project status](#project-status)
- [Detected defect classes](#detected-defect-classes)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run the web application](#run-the-web-application)
- [API reference](#api-reference)
- [Run the computer-vision scripts](#run-the-computer-vision-scripts)
- [Dataset preparation](#dataset-preparation)
- [Training](#training)
- [Evaluation](#evaluation)
- [Configuration notes](#configuration-notes)
- [Limitations and safety notes](#limitations-and-safety-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Technology stack](#technology-stack)
- [Author](#author)

## Project status

### Implemented

- [x] DeepPCB-to-YOLO conversion script
- [x] Train/validation/test dataset preparation
- [x] YOLOv8 training script
- [x] Model evaluation and test scripts
- [x] Image inference
- [x] Offline video inference
- [x] Windows webcam/file-picker inference utility
- [x] Synthetic defect image generator for pipeline testing
- [x] FastAPI inference API
- [x] HTML/CSS/JavaScript dashboard
- [x] Upload-image inspection through the dashboard
- [x] Browser camera preview
- [x] Annotated result image and defect summary

### Planned

- [ ] Send browser camera frames continuously to `/predict-frame`
- [ ] Product ID and QR-code generation/scanning
- [ ] MongoDB inspection-history storage
- [ ] Machine sensor simulation and predictive-maintenance model
- [ ] Combined quality and maintenance dashboard
- [ ] Automated tests and CI/CD
- [ ] Docker image and production deployment
- [ ] Validation on factory data and calibrated acceptance criteria

## Detected defect classes

The Roboflow YOLO dataset used by the trained model defines these six classes:

| Class | Meaning |
|---|---|
| `copper` | Unwanted or extra copper |
| `mousebite` | Notch-like defect near a PCB edge |
| `open` | Broken conductor or trace |
| `pin-hole` | Small hole or void |
| `short` | Unwanted electrical connection |
| `spur` | Unwanted copper protrusion or branch |

The final Roboflow dataset class order is:

```text
0 = copper
1 = mousebite
2 = open
3 = pin-hole
4 = short
5 = spur
```

Always use the class order from the dataset used to train the model. The original DeepPCB conversion dataset uses a different order, so its `data.yaml` must not be mixed with the Roboflow model without retraining or remapping.

## Architecture

```text
Browser dashboard
        |
        | POST /predict (multipart image)
        v
FastAPI backend
        |
        v
Ultralytics YOLO model
models/pcb_yolov8n_v1/weights/best.pt
        |
        v
Detection JSON + annotated JPEG
        |
        v
PASS / FAIL dashboard result
```

The FastAPI application also serves the frontend, so the simplest setup uses one origin:

```text
http://127.0.0.1:8000/
```

## Repository structure

```text
smart-manufacturing-ai/
├── ai/
│   ├── defect_detection/          # Defect-detection area for future modules
│   └── predictive_maintenance/    # Predictive-maintenance area for future modules
├── backend/
│   └── main.py                    # FastAPI app, model loading, inference routes
├── dataset/
│   ├── DeepPCB-master/            # Original dataset; keep local
│   ├── PCB_YOLO/                  # Converted DeepPCB YOLO dataset
│   ├── PCB_YOLO_Roboflow/         # Roboflow YOLO dataset
│   └── synthetic_pcb/             # Generated synthetic images
├── frontend/
│   ├── index.html                 # Dashboard markup
│   ├── script.js                  # Upload, API calls, and UI behavior
│   └── style.css                  # Dashboard styling
├── models/
│   └── pcb_yolov8n_v1/weights/
│       └── best.pt                 # Trained YOLO weights
├── scripts/
│   ├── convert_deeppcb_to_yolo.py
│   ├── create_pcb_video.py
│   ├── create_synthetic_pcb_defects.py
│   ├── detect_pcb_video.py
│   ├── detect_pcb_webcam.py
│   ├── evaluate_pcb_model.py
│   ├── test_pcb_model.py
│   ├── test_synthetic_defects.py
│   └── train_pcb_yolo.py
├── uploads/                       # Local input/output media; keep local
├── runs/                          # Ultralytics prediction/training output
├── .env.example                   # Local configuration template
├── .gitignore                     # Excludes environments and large artifacts
├── requirements.txt
├── yolov8n.pt                     # Base YOLO checkpoint, if available locally
└── README.md
```

## Requirements

- Windows, Linux, or macOS
- Python 3.12 recommended
- Git
- A working webcam for the webcam utility or browser camera preview
- CPU is supported; a CUDA-compatible GPU is recommended for training
- The trained weights at `models/pcb_yolov8n_v1/weights/best.pt`
- The dataset is required only for conversion, training, evaluation, and data-generation workflows

Install the pinned Python dependencies from `requirements.txt`. The environment intentionally is not committed to Git; create it locally instead.

## Installation

From the project root:

```powershell
cd D:\smart-manufacturing-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks script activation for the current session, allow locally created scripts for that session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Verify the important packages and model file:

```powershell
python -c "import ultralytics, fastapi, cv2; print('Ultralytics:', ultralytics.__version__)"
Test-Path models\pcb_yolov8n_v1\weights\best.pt
```

## Run the web application

The backend loads the YOLO model during startup. Run it from the repository root:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open the dashboard at:

```text
http://127.0.0.1:8000/
```

Useful built-in pages:

- Dashboard: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/api/health`

Use **Upload Image** to select a PCB image. The frontend sends it to `/predict`, displays the annotated image, and shows the defect count, highest confidence, class summary, and status.

### Camera behavior

The current dashboard requests browser camera permission and displays a live preview. It does not yet send camera frames continuously to `/predict-frame`; continuous frame-by-frame inspection remains a roadmap item. Use `scripts\detect_pcb_webcam.py` for the current offline webcam/file-picker workflow.

## API reference

### `GET /api/health`

Returns a basic service status response.

Example response:

```json
{
  "status": "online",
  "message": "PCB AI Inspection API is running"
}
```

### `POST /predict`

Accepts an image as multipart form data with the field name `file`.

Example PowerShell request:

```powershell
curl.exe -X POST -F "file=@uploads\images\test_pcb.jpg" http://127.0.0.1:8000/predict
```

The response contains:

| Field | Description |
|---|---|
| `status` | `PASS` when no detections are returned; otherwise `FAIL` |
| `total_defects` | Number of detected bounding boxes |
| `highest_confidence` | Highest detection confidence, from `0` to `1` |
| `defect_counts` | Count grouped by detected class |
| `detections` | Class, confidence, and `x1/y1/x2/y2` box coordinates |
| `image` | Base64-encoded annotated JPEG |

Example response shape:

```json
{
  "status": "FAIL",
  "total_defects": 1,
  "highest_confidence": 0.8732,
  "defect_counts": {"open": 1},
  "detections": [
    {
      "class": "open",
      "confidence": 0.8732,
      "box": {"x1": 120.5, "y1": 80.0, "x2": 240.0, "y2": 155.25}
    }
  ],
  "image": "<base64 JPEG>"
}
```

### `POST /predict-frame`

Accepts the same multipart image format as `/predict`. It is available for camera-frame integration, although the current frontend does not call it continuously yet.

## Run the computer-vision scripts

The scripts currently contain Windows-specific absolute paths beginning with `D:\smart-manufacturing-ai`. Run them from this repository location, or update the path constants before using them from another machine.

### Single-image inference

The sample input is expected at `uploads/images/test_pcb.jpg` and the model at `models/pcb_yolov8n_v1/weights/best.pt`.

```powershell
python scripts\test_pcb_model.py
```

Ultralytics writes the annotated result under `runs/`.

### Generate and detect a test video

First make sure `dataset/PCB_YOLO_Roboflow/test/images` contains test images:

```powershell
python scripts\create_pcb_video.py
python scripts\detect_pcb_video.py
```

The generated source video is `uploads/videos/pcb_test_video.mp4`. Detection output is written below `uploads/videos/detected/pcb_video_detection/`.

### Webcam/file-picker utility

```powershell
python scripts\detect_pcb_webcam.py
```

This Windows utility uses OpenCV and Tkinter, compares confidence levels `0.25`, `0.50`, and `0.70`, and writes results under `runs/threshold_comparison/`. A physical webcam is not required if the script is configured to select an image instead.

### Synthetic defect pipeline

Synthetic images are useful for checking the application pipeline, not for proving model accuracy:

```powershell
python scripts\create_synthetic_pcb_defects.py
python scripts\test_synthetic_defects.py
```

The generator uses a clean DeepPCB template and writes controlled examples such as `synthetic_open.jpg`, `synthetic_short.jpg`, `synthetic_mousebite.jpg`, `synthetic_spur.jpg`, `synthetic_copper.jpg`, and `synthetic_pin-hole.jpg` to `dataset/synthetic_pcb/`.

## Dataset preparation

### DeepPCB source

The conversion script expects the original dataset at:

```text
D:\smart-manufacturing-ai\dataset\DeepPCB-master\PCBData
```

Clone the upstream repository into `dataset/` or place an extracted copy there. The script searches for `*_test.jpg` images and their corresponding annotation files.

DeepPCB annotation format:

```text
x1 y1 x2 y2 class_id
```

The original class IDs are:

```text
1 = open
2 = short
3 = mousebite
4 = spur
5 = copper
6 = pin-hole
```

Convert the dataset:

```powershell
python scripts\convert_deeppcb_to_yolo.py
```

This creates `dataset/PCB_YOLO/` with `images`, `labels`, and `data.yaml` for train/validation/test splits. The converter uses an 80%/10%/10% split and random seed `42`, and does not modify the original DeepPCB files.

### Roboflow dataset

The repository also contains `dataset/PCB_YOLO_Roboflow/`, whose `data.yaml` uses:

```yaml
names: ['copper', 'mousebite', 'open', 'pin-hole', 'short', 'spur']
```

The Roboflow dataset is the class ordering expected by the checked-in trained model. If you replace the dataset or model, verify that the `data.yaml` class order matches the model metadata.

## Training

Training is performed with Ultralytics. The existing training script uses the converted dataset and writes the experiment under `models/pcb_yolov8n_v1/`. Review its path constants and device setting before running it on another machine.

```powershell
python scripts\train_pcb_yolo.py
```

For GPU training, update the script's `device` value to the appropriate CUDA device and ensure a compatible PyTorch installation is available. The checked-in script is configured for CPU training, which is slower but portable.

A typical Ultralytics training configuration used for this project was:

```text
epochs: 30
image size: 512
batch size: 16 in the GPU training run
patience: 10
```

The repository's local training script may use different values, so treat the script as the source of truth for reproducibility.

The trained weights should be available at:

```text
models/pcb_yolov8n_v1/weights/best.pt
```

## Evaluation

Run the evaluation script after confirming that its dataset and model paths point to the intended test set:

```powershell
python scripts\evaluate_pcb_model.py
```

Previously observed dataset-level results were approximately:

```text
Validation: Precision 0.968, Recall 0.968, mAP50 0.987, mAP50-95 0.763
Test:       Precision 0.968, Recall 0.961, mAP50 0.986, mAP50-95 0.769
```

These values are historical experiment results, not a guarantee of production performance. Accuracy can change with dataset version, model weights, confidence threshold, lighting, camera setup, PCB design, and defect severity.

## Configuration notes

`.env.example` documents intended local settings:

```text
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000
MODEL_CONFIDENCE=0.50
MODEL_IMAGE_SIZE=512
```

Copy it for local reference if desired:

```powershell
Copy-Item .env.example .env
```

Important: the current `backend/main.py` does not load `.env` and does not read these variables. Its inference settings are currently hard-coded as `conf=0.50` and `imgsz=512`, and Uvicorn settings are supplied on the command line. Environment-variable support should be added before relying on `.env` for deployment configuration.

Do not commit `.env`, `.venv`, datasets, generated media, or model artifacts unless there is a deliberate storage strategy. The repository `.gitignore` excludes these local and large files.

## PASS / FAIL rule

The current demonstration rule is intentionally simple:

```text
0 detections -> PASS
1 or more detections -> FAIL
```

A production inspection decision should additionally define:

- defect severity and acceptable defect types
- minimum defect size
- confidence thresholds by class
- false-positive and false-negative costs
- product/model-specific acceptance criteria
- lighting, camera, calibration, and image-quality requirements
- human review and audit procedures

This application is a prototype and must not be used as the sole safety or quality-control decision without manufacturing validation.

## Limitations and safety notes

- The model is trained for the PCB defect classes and dataset variants represented in this project; it is not a universal PCB inspection model.
- Synthetic defects are controlled visual transformations and are not a substitute for real factory examples.
- The API currently allows all CORS origins for development convenience. Restrict `allow_origins` before production use.
- Uploaded files are processed in memory by the API; the API does not currently persist inspection history.
- There is no authentication, authorization, rate limiting, file-size policy, or production observability yet.
- The model is loaded at process startup, so a missing or incompatible `best.pt` prevents the API from starting.
- The Windows-specific helper scripts should be refactored to use configurable paths before cross-platform use.

## Troubleshooting

### API does not start

If the traceback ends with `ImportError: cannot import name 'Image' from 'PIL'`, Pillow is incomplete or corrupted inside the virtual environment. Reinstall the pinned package:

```powershell
python -m pip install --force-reinstall --no-cache-dir Pillow==12.3.0
python -c "from PIL import Image; print(Image.__file__)"
```

Check that the model exists:

```powershell
Test-Path models\pcb_yolov8n_v1\weights\best.pt
```

Run the server from the repository root and ensure the virtual environment is active:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If Uvicorn reports `WinError 10048` or says the address is already in use, another process is already using port `8000`. Stop the existing Uvicorn process, or use another port:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

Then open `http://127.0.0.1:8001/`.

### Frontend cannot call the API

Open the dashboard at `http://127.0.0.1:8000/` rather than opening `frontend/index.html` directly. Check `http://127.0.0.1:8000/api/health` and inspect the browser console for errors.

### Camera permission fails

Allow camera access for the browser and use a secure/local origin such as `http://127.0.0.1:8000/`. Stop other applications that may already be using the camera.

### Dataset script finds no images

Confirm that `dataset/DeepPCB-master/PCBData` contains the original DeepPCB folders and files ending in `_test.jpg`. If the project is in a different directory, update the absolute paths in the script.

### Windows path problems

The standalone scripts currently use absolute `D:\smart-manufacturing-ai` paths. Replace those constants with paths for your machine, preferably using `pathlib.Path`, before running them elsewhere.

## Roadmap

1. Move model, threshold, and host settings into validated environment configuration.
2. Add request validation, file-size limits, structured errors, and automated API tests.
3. Implement continuous browser frame capture with throttling and clear latency limits.
4. Add product IDs, QR generation/scanning, and inspection-event schemas.
5. Add MongoDB persistence with indexes and retention policies.
6. Add sensor simulation and a separately evaluated predictive-maintenance model.
7. Add authentication, restricted CORS, logging, monitoring, Docker, and deployment automation.
8. Validate the complete workflow using representative production images and quality-engineering metrics.

## Technology stack

| Area | Technology |
|---|---|
| Language | Python, JavaScript, HTML, CSS |
| Computer vision | OpenCV, Pillow |
| Deep learning | Ultralytics YOLOv8 |
| Dataset | DeepPCB and Roboflow-exported YOLO data |
| Backend | FastAPI, Uvicorn, python-multipart |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Numerical/data tools | NumPy, pandas, Matplotlib |
| Version control | Git and GitHub |
| Future integrations | MongoDB, QR tracking, predictive maintenance, Docker/cloud deployment |

## Author

**Umang P. Kaklotar**  
AI / ML — Smart Manufacturing & PCB Quality Inspection
