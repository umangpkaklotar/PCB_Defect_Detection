// ============================================================
// PCB BARCODE SCANNER
// ============================================================
// Uses the phone camera to decode the Product ID, then performs
// a read-only lookup through the existing FastAPI product API.
// ============================================================

const scannerButton = document.getElementById("scanBarcodeBtn");
const scannerPanel = document.getElementById("barcodeScannerPanel");
const scannerVideo = document.getElementById("barcodeScannerVideo");
const scannerStatus = document.getElementById("barcodeScannerStatus");
const productDetails = document.getElementById("productDetails");
const productNotFound = document.getElementById("productNotFound");
const stopScannerButton = document.getElementById("stopBarcodeScannerBtn");

let barcodeReader = null;
let scannerControls = null;
let lookupInProgress = false;

function setScannerStatus(message) {
    scannerStatus.textContent = message;
}

function clearProductDetails() {
    productDetails.hidden = true;
    productNotFound.hidden = true;
    productDetails.innerHTML = "";
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatDetailValue(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    if (typeof value === "object") {
        return escapeHtml(JSON.stringify(value, null, 2));
    }

    return escapeHtml(value);
}

function showProductDetails(product) {
    const defectCounts = product.defect_counts || {};
    const defectNames = [
        "open",
        "short",
        "mousebite",
        "spur",
        "copper",
        "pin-hole"
    ];
    const defectCards = defectNames.map((defectName) => `
        <div class="scanner-defect-card">
            <span>${defectName}</span>
            <strong>${formatDetailValue(defectCounts[defectName] || 0)}</strong>
        </div>
    `).join("");

    productDetails.innerHTML = `
        <div class="scanner-product-heading">
            <span>PCB Product ID</span>
            <strong>${formatDetailValue(product.product_id)}</strong>
        </div>

        <div class="scanner-defects-section">
            <h3>PCB Defect Counts</h3>
            <div class="scanner-defect-grid">
                ${defectCards}
            </div>
        </div>

        <div class="product-detail-row">
            <span>Product Type</span>
            <strong>${formatDetailValue(product.product_type)}</strong>
        </div>
        <div class="product-detail-row">
            <span>Status</span>
            <strong>${formatDetailValue(product.status)}</strong>
        </div>
        <div class="product-detail-row">
            <span>Inspection Count</span>
            <strong>${formatDetailValue(product.inspection_count)}</strong>
        </div>
        <div class="product-detail-row product-detail-block">
            <span>Last Inspection</span>
            <pre>${formatDetailValue(product.last_inspection)}</pre>
        </div>
        <div class="scanner-barcode-result">
            <span>Existing Barcode</span>
            <img
                class="scanned-product-barcode"
                src="${API_URL}${product.barcode_url || `/api/products/${encodeURIComponent(product.product_id)}/barcode`}"
                alt="Existing barcode for ${formatDetailValue(product.product_id)}"
            >
        </div>
    `;

    productDetails.hidden = false;
}

async function lookupProduct(productId) {
    const response = await fetch(
        `${API_URL}/api/products/${encodeURIComponent(productId)}`
    );
    const data = await response.json();

    if (response.status === 404) {
        throw new Error("PCB not found");
    }

    if (!response.ok) {
        throw new Error(data.detail || "Could not look up the PCB.");
    }

    return data;
}

async function handleBarcodeScan(result) {
    if (lookupInProgress || !result) {
        return;
    }

    const productId = result.getText().trim();
    if (!productId) {
        return;
    }

    lookupInProgress = true;
    stopScanner();
    setScannerStatus(`Barcode detected: ${productId}`);
    clearProductDetails();

    try {
        const product = await lookupProduct(productId);
        showProductDetails(product);
        setScannerStatus("PCB details loaded");
    } catch (error) {
        productNotFound.textContent = error.message;
        productNotFound.hidden = false;
        setScannerStatus("Scan complete");
    } finally {
        lookupInProgress = false;
    }
}

function stopScanner() {
    if (scannerControls) {
        scannerControls.stop();
        scannerControls = null;
    }

    if (barcodeReader) {
        barcodeReader.reset();
    }

    scannerVideo.srcObject = null;
}

async function startScanner() {
    clearProductDetails();
    scannerPanel.hidden = false;
    setScannerStatus("Starting camera...");

    if (!window.isSecureContext || !navigator.mediaDevices) {
        setScannerStatus("Camera permission required");
        productNotFound.textContent =
            "Open the HTTPS phone URL to use the camera scanner.";
        productNotFound.hidden = false;
        return;
    }

    try {
        barcodeReader = new ZXingBrowser.BrowserMultiFormatReader(
            undefined,
            250
        );
        scannerControls = await barcodeReader.decodeFromConstraints(
            {
                video: {
                    facingMode: { exact: "environment" },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            },
            scannerVideo,
            (result, error) => {
                if (result) {
                    handleBarcodeScan(result);
                } else if (error && error.name !== "NotFoundException") {
                    console.debug("Barcode scan waiting:", error);
                }
            }
        );
        setScannerStatus("Point the phone camera at a PCB barcode");
    } catch (error) {
        stopScanner();
        if (
            error.name === "NotAllowedError" ||
            error.name === "PermissionDeniedError"
        ) {
            setScannerStatus("Camera permission required");
            productNotFound.textContent =
                "Allow camera access in the browser settings, then try again.";
        } else {
            setScannerStatus("Camera could not be started.");
            productNotFound.textContent =
                "The rear camera is unavailable on this device.";
        }
        productNotFound.hidden = false;
        console.error("Barcode scanner error:", error);
    }
}

scannerButton.addEventListener("click", () => {
    if (scannerPanel.hidden) {
        startScanner();
    } else {
        stopScanner();
        scannerPanel.hidden = true;
        setScannerStatus("Scanner closed");
    }
});

stopScannerButton.addEventListener("click", () => {
    stopScanner();
    scannerPanel.hidden = true;
    setScannerStatus("Scanner stopped");
});

window.addEventListener("beforeunload", stopScanner);
