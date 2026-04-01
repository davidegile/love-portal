const waitingPanel = document.getElementById("waiting-panel");
const portalPanel = document.getElementById("portal-panel");
const letterPanel = document.getElementById("letter-panel");
const visionMessage = document.getElementById("vision-message");
const scoreValue = document.getElementById("score-value");
const pinDisplay = document.getElementById("pin-display");
const pinMessage = document.getElementById("pin-message");
const hintBox = document.getElementById("hint-box");
const letterTitle = document.getElementById("letter-title");
const letterContent = document.getElementById("letter-content");
const fullscreenEntry = document.getElementById("fullscreen-entry");
const cameraPreview = document.getElementById("camera-preview");

let currentPin = "";
let currentPhase = "waiting_for_heart";
let lastCameraSuccessAt = 0;

function setActivePanel(phase) {
    waitingPanel.classList.toggle("panel-active", phase === "waiting_for_heart");
    portalPanel.classList.toggle("panel-active", phase === "portal_open");
    letterPanel.classList.toggle("panel-active", phase === "letter_unlocked");
    currentPhase = phase;
}

function renderPin() {
    const padded = currentPin.padEnd(4, "-");
    pinDisplay.textContent = padded.split("").join(" ");
}

async function fetchState() {
    const response = await fetch("/api/state");
    if (!response.ok) {
        return;
    }

    const data = await response.json();
    visionMessage.textContent = data.vision_message || data.status_message;
    scoreValue.textContent = Number(data.last_detection_score || 0).toFixed(3);
    hintBox.textContent = data.hint || "";
    pinMessage.textContent = data.status_message || "";
    letterTitle.textContent = data.letter_title || "Per te";
    letterContent.innerHTML = data.letter_html || "";
    setActivePanel(data.phase);
}

function refreshCameraPreview() {
    const now = Date.now();
    cameraPreview.src = `/video-frame?t=${now}`;
}

cameraPreview.addEventListener("load", () => {
    lastCameraSuccessAt = Date.now();
});

cameraPreview.addEventListener("error", () => {
    if (Date.now() - lastCameraSuccessAt > 2500) {
        visionMessage.textContent = "Webcam attiva, ma anteprima non ancora pronta.";
    }
});

async function submitPin() {
    if (currentPin.length !== 4) {
        pinMessage.textContent = "Servono quattro cifre.";
        return;
    }

    const response = await fetch("/api/pin/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin: currentPin }),
    });
    const data = await response.json();
    pinMessage.textContent = data.message || "";
    hintBox.textContent = data.hint || "";
    currentPin = "";
    renderPin();
    await fetchState();
}

function handleDigitInput(value) {
    if (currentPhase !== "portal_open") {
        return;
    }

    if (value === "clear") {
        currentPin = "";
        renderPin();
        return;
    }

    if (value === "submit") {
        submitPin();
        return;
    }

    if (currentPin.length < 4) {
        currentPin += value;
        renderPin();
    }
}

document.getElementById("keypad").addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) {
        return;
    }

    if (button.dataset.digit) {
        handleDigitInput(button.dataset.digit);
        return;
    }

    if (button.dataset.action) {
        handleDigitInput(button.dataset.action);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key >= "0" && event.key <= "9") {
        handleDigitInput(event.key);
    } else if (event.key === "Backspace") {
        currentPin = currentPin.slice(0, -1);
        renderPin();
    } else if (event.key === "Enter") {
        submitPin();
    }
});

fullscreenEntry.addEventListener("click", async () => {
    if (document.documentElement.requestFullscreen) {
        try {
            await document.documentElement.requestFullscreen();
        } catch (_) {
            // Ignore browser fullscreen failures and keep experience usable.
        }
    }
    fullscreenEntry.style.display = "none";
});

renderPin();
fetchState();
refreshCameraPreview();
setInterval(fetchState, 1000);
setInterval(refreshCameraPreview, 180);
