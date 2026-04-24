// === Online Exam Proctoring Script ===
// Requirements: face-api.js (CDN), Django backend endpoint for violations

// --- Config ---
const VIOLATION_LIMIT = 6;
let violationCount = 0;
let autoSubmitTriggered = false;

// --- Utility: Log violation and send to backend ---
function logViolation(type, details = "") {
  violationCount++;
  fetch("/api/log-violation/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ type, details, count: violationCount }),
  });
  alert(`Violation detected: ${type}`);
  if (violationCount >= VIOLATION_LIMIT && !autoSubmitTriggered) {
    autoSubmitTriggered = true;
    alert("Too many violations. Exam will be auto-submitted.");
    document.getElementById("exam-form").submit();
  }
}

function getCSRFToken() {
  let m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : "";
}

// --- Proctoring logic: Only activate on student exam attempt page ---
function enableExamProctoring() {
  // --- Fullscreen ---
  function enterFullscreen() {
    let el = document.documentElement;
    if (el.requestFullscreen) el.requestFullscreen();
    else if (el.mozRequestFullScreen) el.mozRequestFullScreen();
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    else if (el.msRequestFullscreen) el.msRequestFullscreen();
  }
  function isFullscreen() {
    return (
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement
    );
  }
  enterFullscreen();
  document.addEventListener("fullscreenchange", () => {
    if (!isFullscreen()) logViolation("Fullscreen exited");
  });

  // --- Tab Switching ---
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) logViolation("Tab switched");
  });

  // --- Disable Cheating Actions ---
  document.addEventListener("contextmenu", (e) => e.preventDefault());
  document.addEventListener("copy", (e) => e.preventDefault());
  document.addEventListener("cut", (e) => e.preventDefault());
  document.addEventListener("paste", (e) => e.preventDefault());
  document.addEventListener("keydown", (e) => {
    if (
      (e.ctrlKey && ["c", "v", "x", "u"].includes(e.key.toLowerCase())) ||
      e.key === "F12" ||
      (e.altKey && e.key === "Tab")
    ) {
      e.preventDefault();
      logViolation("Prohibited key/shortcut");
    }
  });

  // --- Webcam & Face Detection ---
  async function setupWebcamProctoring() {
    const video = document.createElement("video");
    video.autoplay = true;
    video.style =
      "position:fixed;bottom:10px;right:10px;width:180px;height:140px;z-index:9999;border:2px solid #007bff;background:#000;";
    document.body.appendChild(video);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      // Webcam enabled: show exam UI and start timer
      if (typeof startExamUI === 'function') {
        startExamUI();
        if (typeof showExamFirstQuestion === 'function') showExamFirstQuestion();
      }
    } catch (err) {
      logViolation("Webcam access denied");
      return;
    }
    await loadFaceApiModels();
    monitorFace(video);
  }

  async function loadFaceApiModels() {
    if (!window.faceapi) {
      await new Promise((resolve) => {
        const script = document.createElement("script");
        script.src =
          "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js";
        script.onload = resolve;
        document.head.appendChild(script);
      });
    }
    await faceapi.nets.tinyFaceDetector.loadFromUri("/static/models");
    await faceapi.nets.faceLandmark68Net.loadFromUri("/static/models");
    await faceapi.nets.faceRecognitionNet.loadFromUri("/static/models");
  }

  async function monitorFace(video) {
    let lastViolation = 0;
    setInterval(async () => {
      const detections = await faceapi
        .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks();
      if (!detections.length) {
        if (Date.now() - lastViolation > 5000) {
          logViolation("No face detected");
          lastViolation = Date.now();
        }
      } else if (detections.length > 1) {
        logViolation("Multiple faces detected");
      } else {
        // Head pose estimation (basic)
        const landmarks = detections[0].landmarks;
        const nose = landmarks.getNose();
        const leftEye = landmarks.getLeftEye();
        const rightEye = landmarks.getRightEye();
        // Simple check: if nose is far left/right of eyes, user is looking away
        if (nose[3].x < leftEye[0].x || nose[3].x > rightEye[3].x) {
          logViolation("Looking away from screen");
        }
      }
    }, 3000);
  }

  setupWebcamProctoring();
}

// Only enable proctoring if on student exam attempt page
document.addEventListener("DOMContentLoaded", () => {
  if (
    document.getElementById("exam-form") &&
    window.location.pathname.includes("/dashboard/student/exam/")
  ) {
    enableExamProctoring();
  }
});
