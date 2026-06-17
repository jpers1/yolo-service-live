const apiKeyInput = document.querySelector("#api-key");
const startButton = document.querySelector("#start-button");
const stopButton = document.querySelector("#stop-button");
const video = document.querySelector("#preview");
const overlay = document.querySelector("#overlay");
const capture = document.querySelector("#capture");
const cameraStatus = document.querySelector("#camera-status");
const requestStatus = document.querySelector("#request-status");
const latencyStatus = document.querySelector("#latency-status");
const detectionStatus = document.querySelector("#detection-status");
const errorStatus = document.querySelector("#error-status");

const overlayContext = overlay.getContext("2d");
const captureContext = capture.getContext("2d");

let stream = null;
let running = false;
let inFlight = false;
let timerId = null;

startButton.addEventListener("click", startDemo);
stopButton.addEventListener("click", stopDemo);
window.addEventListener("resize", () => {
  syncOverlaySize();
  clearOverlay();
});

async function startDemo() {
  clearError();
  const apiKey = apiKeyInput.value.trim();
  if (!apiKey) {
    showError("Enter an API key before starting the demo.");
    return;
  }

  try {
    cameraStatus.textContent = "requesting access";
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();
    running = true;
    startButton.disabled = true;
    stopButton.disabled = false;
    cameraStatus.textContent = "running";
    requestStatus.textContent = "idle";
    syncOverlaySize();
    scheduleNextFrame(0);
  } catch (error) {
    stopTracks();
    cameraStatus.textContent = "stopped";
    showError(`Camera unavailable or denied: ${error.message}`);
  }
}

function stopDemo() {
  running = false;
  if (timerId !== null) {
    window.clearTimeout(timerId);
    timerId = null;
  }
  stopTracks();
  clearOverlay();
  startButton.disabled = false;
  stopButton.disabled = true;
  cameraStatus.textContent = "stopped";
  requestStatus.textContent = "idle";
  detectionStatus.textContent = "0";
}

function stopTracks() {
  if (stream) {
    for (const track of stream.getTracks()) {
      track.stop();
    }
  }
  stream = null;
  video.srcObject = null;
}

function scheduleNextFrame(delayMs = 1000) {
  if (!running) {
    return;
  }
  timerId = window.setTimeout(processFrame, delayMs);
}

async function processFrame() {
  if (!running) {
    return;
  }
  if (inFlight) {
    scheduleNextFrame(250);
    return;
  }

  const apiKey = apiKeyInput.value.trim();
  if (!apiKey) {
    requestStatus.textContent = "paused";
    showError("API key was cleared. Enter a key and restart.");
    stopDemo();
    return;
  }

  inFlight = true;
  requestStatus.textContent = "sending";
  clearError();
  const startedAt = performance.now();

  try {
    const imageUrl = captureFrame();
    const response = await fetch("/v1/vision/detections", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "yolo11n-coco",
        image: { url: imageUrl },
        include_normalized_boxes: true,
      }),
    });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(errorMessage(body, response.status));
    }

    const elapsedMs = Math.round(performance.now() - startedAt);
    latencyStatus.textContent = `${elapsedMs} ms`;
    requestStatus.textContent = "ok";
    detectionStatus.textContent = String(body.detections.length);
    drawDetections(body);
  } catch (error) {
    requestStatus.textContent = "error";
    showError(error.message);
  } finally {
    inFlight = false;
    scheduleNextFrame(1000);
  }
}

function captureFrame() {
  const sourceWidth = video.videoWidth;
  const sourceHeight = video.videoHeight;
  if (!sourceWidth || !sourceHeight) {
    throw new Error("Camera frame is not ready yet.");
  }

  const maxWidth = 416;
  const scale = Math.min(1, maxWidth / sourceWidth);
  capture.width = Math.round(sourceWidth * scale);
  capture.height = Math.round(sourceHeight * scale);
  captureContext.drawImage(video, 0, 0, capture.width, capture.height);
  return capture.toDataURL("image/jpeg", 0.82);
}

function syncOverlaySize() {
  const rect = video.getBoundingClientRect();
  const pixelRatio = window.devicePixelRatio || 1;
  overlay.width = Math.max(1, Math.round(rect.width * pixelRatio));
  overlay.height = Math.max(1, Math.round(rect.height * pixelRatio));
  overlay.style.width = `${rect.width}px`;
  overlay.style.height = `${rect.height}px`;
}

function clearOverlay() {
  overlayContext.clearRect(0, 0, overlay.width, overlay.height);
}

function drawDetections(payload) {
  syncOverlaySize();
  clearOverlay();
  overlayContext.lineWidth = 3;
  overlayContext.strokeStyle = "#f6d365";
  overlayContext.fillStyle = "#f6d365";
  overlayContext.font = "16px Trebuchet MS, sans-serif";

  for (const detection of payload.detections) {
    const box = displayBox(detection, payload.source);
    overlayContext.strokeRect(box.x, box.y, box.width, box.height);
    const confidence = Math.round(detection.confidence * 100);
    const label = `${detection.class_name} ${confidence}%`;
    const labelY = Math.max(18, box.y - 8);
    overlayContext.fillText(label, box.x, labelY);
  }
}

function displayBox(detection, source) {
  if (Array.isArray(detection.box_normalized_xyxy)) {
    const [x1, y1, x2, y2] = detection.box_normalized_xyxy;
    return {
      x: x1 * overlay.width,
      y: y1 * overlay.height,
      width: (x2 - x1) * overlay.width,
      height: (y2 - y1) * overlay.height,
    };
  }

  const [x1, y1, x2, y2] = detection.box_xyxy;
  const sourceWidth = source.width || overlay.width;
  const sourceHeight = source.height || overlay.height;
  return {
    x: (x1 / sourceWidth) * overlay.width,
    y: (y1 / sourceHeight) * overlay.height,
    width: ((x2 - x1) / sourceWidth) * overlay.width,
    height: ((y2 - y1) / sourceHeight) * overlay.height,
  };
}

function errorMessage(body, statusCode) {
  if (body && body.error && body.error.message) {
    return `${statusCode}: ${body.error.message}`;
  }
  return `${statusCode}: request failed`;
}

function showError(message) {
  errorStatus.textContent = message;
}

function clearError() {
  errorStatus.textContent = "";
}
