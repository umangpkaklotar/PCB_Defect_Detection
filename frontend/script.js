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
const newProductBtn =
    document.getElementById("newProductBtn");
const currentProductId =
    document.getElementById("currentProductId");

const cameraBtn = document.getElementById("cameraBtn");
const stopCameraBtn = document.getElementById("stopCameraBtn");

const previewImage = document.getElementById("previewImage");
const cameraVideo = document.getElementById("cameraVideo");
const cameraResultImage =
    document.getElementById("cameraResultImage");
const cameraCanvas =
    document.getElementById("cameraCanvas");

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
let cameraPredictionInterval = null;
let cameraPredictionInFlight = false;

const CAMERA_API_URL =
    "http://127.0.0.1:8000";

const CAMERA_FRAME_INTERVAL = 750;

let activeProductId = null;


// ============================================================
// UPLOAD BUTTON
// ============================================================

uploadBtn.addEventListener("click", function () {

    imageInput.click();

});


// ============================================================
// PRODUCT CREATION
// ============================================================

newProductBtn.addEventListener(
    "click",
    async function () {

        try {
            await createProduct();

        } catch (error) {

            console.error(
                "Product creation error:",
                error
            );

            currentProductId.textContent =
                "Unavailable";

            alert(
                `Could not create PCB product.\n\n${error.message}`
            );

        } finally {

            newProductBtn.disabled =
                false;

            newProductBtn.textContent =
                "New PCB Product";

        }

    }
);


async function createProduct() {

    newProductBtn.disabled =
        true;

    newProductBtn.textContent =
        "Creating...";

    try {

        const response =
            await fetch(
                `${API_URL}/api/products`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        product_type: "PCB"
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                `Server returned ${response.status}`
            );
        }

        activeProductId =
            data.product_id;

        currentProductId.textContent =
            activeProductId;

        inspectionStatus.textContent =
            `${activeProductId} ready for inspection`;

        return data;

    } finally {

        newProductBtn.disabled =
            false;

        newProductBtn.textContent =
            "New PCB Product";

    }

}


async function ensureActiveProduct() {

    if (activeProductId) {
        return activeProductId;
    }

    const product =
        await createProduct();

    return product.product_id;
}


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

            const productId =
                await ensureActiveProduct();

            formData.append(
                "product_id",
                productId
            );

            formData.append(
                "new_product_on_change",
                "true"
            );

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

            if (data.product_id) {
                activeProductId = data.product_id;
                currentProductId.textContent = activeProductId;
            }

            if (data.product_message) {
                inspectionStatus.textContent =
                    data.product_message;
            }


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
                    `Inspection Complete${
                        data.product_message
                            ? ` - ${data.product_message}`
                            : ""
                    }`;

            } else {

                showFailResult();

                inspectionStatus.textContent =
                    `Defect Detected${
                        data.product_message
                            ? ` - ${data.product_message}`
                            : ""
                    }`;

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

        await ensureActiveProduct();

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

        cameraResultImage.hidden =
            true;

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

        startCameraPredictionLoop();


    } catch (error) {

        console.error(
            "Camera Error:",
            error
        );


        alert(
            "Camera access could not be started.\n\n" +
            "Please allow camera permission."
        );

        inspectionStatus.textContent =
            "Camera unavailable";

        resultMessage.textContent =
            "Camera permission was denied or no camera is available.";

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

    if (cameraPredictionInterval) {

        clearInterval(
            cameraPredictionInterval
        );

        cameraPredictionInterval = null;
    }

    cameraPredictionInFlight =
        false;

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

    cameraResultImage.src =
        "";

    cameraResultImage.hidden =
        true;

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
// CAMERA FRAME PREDICTION
// ============================================================

function startCameraPredictionLoop() {

    if (cameraPredictionInterval) {
        return;
    }

    captureCameraFrame();

    cameraPredictionInterval =
        setInterval(
            captureCameraFrame,
            CAMERA_FRAME_INTERVAL
        );

}


async function captureCameraFrame() {

    if (
        !cameraStream ||
        cameraPredictionInFlight ||
        cameraVideo.readyState < 2 ||
        !cameraVideo.videoWidth ||
        !cameraVideo.videoHeight
    ) {
        return;
    }

    cameraPredictionInFlight =
        true;

    cameraCanvas.width =
        cameraVideo.videoWidth;

    cameraCanvas.height =
        cameraVideo.videoHeight;

    const context =
        cameraCanvas.getContext("2d");

    context.drawImage(
        cameraVideo,
        0,
        0,
        cameraCanvas.width,
        cameraCanvas.height
    );

    try {

        const blob =
            await new Promise(
                function (resolve) {

                    cameraCanvas.toBlob(
                        resolve,
                        "image/jpeg",
                        0.85
                    );

                }
            );

        if (!blob) {
            throw new Error(
                "Could not capture camera frame."
            );
        }

        const formData =
            new FormData();

        formData.append(
            "file",
            blob,
            "camera-frame.jpg"
        );

        formData.append(
            "product_id",
            activeProductId
        );

        formData.append(
            "new_product_on_change",
            "false"
        );

        const response =
            await fetch(
                `${CAMERA_API_URL}/predict-frame`,
                {
                    method: "POST",
                    body: formData
                }
            );

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const data =
            await response.json();

        if (!cameraStream) {
            return;
        }

        if (data.product_id) {
            activeProductId = data.product_id;
            currentProductId.textContent = activeProductId;
        }

        if (data.image) {

            cameraResultImage.src =
                `data:image/jpeg;base64,${data.image}`;

            cameraResultImage.hidden =
                false;

        }

        totalDefects.textContent =
            data.total_defects || 0;

        updateConfidence(
            data.highest_confidence || 0
        );

        updateDefectSummary(
            data.defect_counts || {}
        );

        if (data.status === "PASS") {

            showPassResult();
            inspectionStatus.textContent =
                "Live Camera - PASS";

        } else {

            showFailResult();
            inspectionStatus.textContent =
                "Live Camera - Defect Detected";

        }

    } catch (error) {

        console.error(
            "Camera prediction error:",
            error
        );

        inspectionStatus.textContent =
            "Camera API Error";

        resultBox.className =
            "result-box fail";

        resultIcon.textContent =
            "⚠";

        resultTitle.textContent =
            "Camera Inspection Error";

        resultMessage.textContent =
            "Could not connect to the camera inspection server.";

        statusText.textContent =
            "ERROR";

    } finally {

        cameraPredictionInFlight =
            false;

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

    const defectNames = [
        "open",
        "short",
        "mousebite",
        "spur",
        "copper",
        "pin-hole"
    ];

    const defectEntries = defectNames.map(
        function (defectName) {
            return [
                defectName,
                Number(defects && defects[defectName] || 0)
            ];
        }
    );

    const totalDetected = defectEntries.reduce(
        function (total, entry) {
            return total + entry[1];
        },
        0
    );


    // --------------------------------------------------------
    // Display all six defect classes
    // --------------------------------------------------------

    defectEntries.forEach(
        function (entry) {

            const defectName = entry[0];
            const count = entry[1];


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


            defectList.appendChild(item);

        }
    );

    totalDefects.textContent =
        totalDetected;


    // --------------------------------------------------------
    // PASS / FAIL
    // --------------------------------------------------------

    if (totalDetected > 0) {

        showFailResult();

    } else {

        showPassResult();

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