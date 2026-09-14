// ============================================================
// PCB AI QUALITY INSPECTION
// JAVASCRIPT
// ============================================================
//
// PURPOSE:
// Frontend + FastAPI + YOLO model connection.
//
// FLOW:
//
// Image Upload
//      ↓
// JavaScript
//      ↓
// FastAPI /predict
//      ↓
// YOLO best.pt
//      ↓
// Detection
//      ↓
// JSON Result
//      ↓
// Frontend UI
//
// ============================================================


// ============================================================
// FASTAPI BACKEND
// ============================================================

// When FastAPI serves this page, an empty base URL keeps API calls same-origin.
// The localhost fallback also lets the page work when opened directly as a file.
const API_URL =
    window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin;


// ============================================================
// HTML ELEMENTS
// ============================================================

const uploadBtn = document.getElementById("uploadBtn");
const imageInput = document.getElementById("imageInput");

const cameraBtn = document.getElementById("cameraBtn");
const stopCameraBtn = document.getElementById("stopCameraBtn");

const previewImage = document.getElementById("previewImage");
const cameraVideo = document.getElementById("cameraVideo");

const placeholder = document.getElementById("placeholder");
const cameraControls = document.getElementById("cameraControls");

const inspectionStatus =
    document.getElementById("inspectionStatus");

const resultBox =
    document.getElementById("resultBox");

const resultIcon =
    document.getElementById("resultIcon");

const resultTitle =
    document.getElementById("resultTitle");

const resultMessage =
    document.getElementById("resultMessage");

const totalDefects =
    document.getElementById("totalDefects");

const highestConfidence =
    document.getElementById("highestConfidence");

const statusText =
    document.getElementById("statusText");

const defectList =
    document.getElementById("defectList");


// ============================================================
// CAMERA STREAM
// ============================================================

let cameraStream = null;


// ============================================================
// UPLOAD BUTTON
// ============================================================

uploadBtn.addEventListener("click", function () {

    imageInput.click();

});


// ============================================================
// IMAGE UPLOAD
// ============================================================
//
// User image select kare tyare:
//
// Image
//   ↓
// FastAPI
//   ↓
// YOLO
//   ↓
// Result
//
// ============================================================

imageInput.addEventListener(
    "change",
    async function () {

        const file = imageInput.files[0];


        if (!file) {
            return;
        }


        // ----------------------------------------------------
        // Validate file
        // ----------------------------------------------------

        if (!file.type.startsWith("image/")) {

            alert(
                "Please select a valid PCB image."
            );

            return;
        }


        // ----------------------------------------------------
        // Show original image
        // ----------------------------------------------------

        const imageURL =
            URL.createObjectURL(file);

        previewImage.src =
            imageURL;

        previewImage.hidden =
            false;

        placeholder.hidden =
            true;


        // ----------------------------------------------------
        // Stop camera
        // ----------------------------------------------------

        stopCamera();


        // ----------------------------------------------------
        // Show processing
        // ----------------------------------------------------

        inspectionStatus.textContent =
            "AI Inspecting...";

        showWaitingResult(
            "AI Inspection in Progress"
        );


        // ----------------------------------------------------
        // Prepare image for API
        // ----------------------------------------------------

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        try {

            console.log(
                "Sending image to FastAPI..."
            );


            // ------------------------------------------------
            // Call FastAPI
            // ------------------------------------------------

            const response =
                await fetch(
                    `${API_URL}/predict`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            // ------------------------------------------------
            // Check API
            // ------------------------------------------------

            if (!response.ok) {

                throw new Error(
                    `Server returned ${response.status}`
                );

            }


            // ------------------------------------------------
            // Get JSON
            // ------------------------------------------------

            const data =
                await response.json();


            console.log(
                "YOLO Result:",
                data
            );


            // ------------------------------------------------
            // Display YOLO annotated image
            // ------------------------------------------------

            if (data.image) {

                previewImage.src =
                    `data:image/jpeg;base64,${data.image}`;

            }


            // ------------------------------------------------
            // Total defects
            // ------------------------------------------------

            totalDefects.textContent =
                data.total_defects;


            // ------------------------------------------------
            // Highest confidence
            // ------------------------------------------------

            updateConfidence(
                data.highest_confidence
            );


            // ------------------------------------------------
            // Defect summary
            // ------------------------------------------------

            updateDefectSummary(
                data.defect_counts
            );


            // ------------------------------------------------
            // PASS / FAIL
            // ------------------------------------------------

            if (data.status === "PASS") {

                showPassResult();

                inspectionStatus.textContent =
                    "Inspection Complete";

            } else {

                showFailResult();

                inspectionStatus.textContent =
                    "Defect Detected";

            }


        } catch (error) {

            console.error(
                "Inspection Error:",
                error
            );


            // ------------------------------------------------
            // Error UI
            // ------------------------------------------------

            inspectionStatus.textContent =
                "Inspection Error";


            resultBox.className =
                "result-box fail";


            resultIcon.textContent =
                "⚠";


            resultTitle.textContent =
                "Inspection Failed";


            resultMessage.textContent =
                "Could not connect to AI inspection server.";


            statusText.textContent =
                "ERROR";


            alert(
                "Could not connect to FastAPI.\n\n" +
                "Make sure this is running:\n\n" +
                "uvicorn backend.main:app --reload"
            );

        }

    }
);


// ============================================================
// START CAMERA
// ============================================================

cameraBtn.addEventListener(
    "click",
    async function () {

        await startCamera();

    }
);


async function startCamera() {

    try {

        // ----------------------------------------------------
        // Request camera
        // ----------------------------------------------------

        cameraStream =
            await navigator.mediaDevices.getUserMedia({
                video: {
                    width: {
                        ideal: 1280
                    },
                    height: {
                        ideal: 720
                    }
                },
                audio: false
            });


        // ----------------------------------------------------
        // Show camera
        // ----------------------------------------------------

        cameraVideo.srcObject =
            cameraStream;

        cameraVideo.hidden =
            false;

        previewImage.hidden =
            true;

        placeholder.hidden =
            true;

        cameraControls.hidden =
            false;

        cameraBtn.disabled =
            true;


        inspectionStatus.textContent =
            "Live Camera";


        showWaitingResult(
            "Live Camera Ready"
        );


    } catch (error) {

        console.error(
            "Camera Error:",
            error
        );


        alert(
            "Camera access could not be started.\n\n" +
            "Please allow camera permission."
        );

    }

}


// ============================================================
// STOP CAMERA
// ============================================================

stopCameraBtn.addEventListener(
    "click",
    function () {

        stopCamera();

    }
);


function stopCamera() {

    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(
                function (track) {

                    track.stop();

                }
            );

        cameraStream = null;
    }


    cameraVideo.srcObject =
        null;

    cameraVideo.hidden =
        true;

    cameraControls.hidden =
        true;

    cameraBtn.disabled =
        false;


    if (
        imageInput.files &&
        imageInput.files.length > 0
    ) {

        previewImage.hidden =
            false;

        inspectionStatus.textContent =
            "Image Ready";

    } else {

        placeholder.hidden =
            false;

        inspectionStatus.textContent =
            "Waiting for PCB...";

    }

}


// ============================================================
// WAITING RESULT
// ============================================================

function showWaitingResult(message) {

    resultBox.className =
        "result-box waiting";


    resultIcon.textContent =
        "—";


    resultTitle.textContent =
        message;


    resultMessage.textContent =
        "AI inspection result will appear here.";


    totalDefects.textContent =
        "0";


    highestConfidence.textContent =
        "0%";


    statusText.textContent =
        "Waiting";


    defectList.innerHTML = `
        <div class="no-defects">
            No inspection data available.
        </div>
    `;

}


// ============================================================
// PASS RESULT
// ============================================================

function showPassResult() {

    resultBox.className =
        "result-box pass";


    resultIcon.textContent =
        "✓";


    resultTitle.textContent =
        "PCB PASSED";


    resultMessage.textContent =
        "No defect detected in this PCB.";


    statusText.textContent =
        "PASS";

}


// ============================================================
// FAIL RESULT
// ============================================================

function showFailResult() {

    resultBox.className =
        "result-box fail";


    resultIcon.textContent =
        "✕";


    resultTitle.textContent =
        "PCB DEFECTIVE";


    resultMessage.textContent =
        "One or more defects detected.";


    statusText.textContent =
        "FAIL";

}


// ============================================================
// UPDATE DEFECT SUMMARY
// ============================================================

function updateDefectSummary(defects) {

    defectList.innerHTML =
        "";


    // --------------------------------------------------------
    // No defects
    // --------------------------------------------------------

    if (
        !defects ||
        Object.keys(defects).length === 0
    ) {

        defectList.innerHTML = `
            <div class="no-defects">
                No defects detected.
            </div>
        `;

        totalDefects.textContent =
            "0";

        showPassResult();

        return;
    }


    // --------------------------------------------------------
    // Create defect items
    // --------------------------------------------------------

    Object.keys(defects).forEach(
        function (defectName) {

            const count =
                defects[defectName];


            const item =
                document.createElement("div");


            item.className =
                "defect-item";


            item.innerHTML = `
                <span class="defect-name">
                    ${defectName}
                </span>

                <span class="defect-count">
                    ${count}
                </span>
            `;


            defectList.appendChild(
                item
            );

        }
    );


    // --------------------------------------------------------
    // PASS / FAIL
    // --------------------------------------------------------

    if (
        Object.keys(defects).length > 0
    ) {

        showFailResult();

    }

}


// ============================================================
// UPDATE CONFIDENCE
// ============================================================

function updateConfidence(confidence) {

    const percentage =
        Math.round(
            confidence * 100
        );


    highestConfidence.textContent =
        percentage + "%";

}


// ============================================================
// INITIAL STATE
// ============================================================

showWaitingResult(
    "Waiting for Inspection"
);


// ============================================================
// STOP CAMERA WHEN PAGE CLOSES
// ============================================================

window.addEventListener(
    "beforeunload",
    function () {

        stopCamera();

    }
);