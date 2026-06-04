import { useEffect, useRef, useState } from "react";

const CAPTURE_INTERVAL_MS = 150;
const JPEG_QUALITY = 0.68;

export default function WebcamPanel({ active, onFrame }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const [cameraState, setCameraState] = useState("idle");

  useEffect(() => {
    if (!active) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      if (videoRef.current) videoRef.current.srcObject = null;
      return undefined;
    }

    let cancelled = false;

    navigator.mediaDevices
      .getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        streamRef.current = stream;
        setCameraState("live");
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }

        intervalRef.current = window.setInterval(() => {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          if (!video || !canvas || video.readyState < 2) return;

          canvas.width = video.videoWidth || 640;
          canvas.height = video.videoHeight || 480;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          canvas.toBlob(
            (blob) => {
              if (blob) onFrame?.(blob);
            },
            "image/jpeg",
            JPEG_QUALITY,
          );
        }, CAPTURE_INTERVAL_MS);
      })
      .catch(() => setCameraState("blocked"));

    return () => {
      cancelled = true;
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    };
  }, [active, onFrame]);

  const visibleCameraState =
    active && cameraState === "idle" ? "starting" : active ? cameraState : "idle";

  return (
    <section className="webcamPanel" aria-label="Webcam stream">
      <div className="videoShell">
        <video ref={videoRef} muted playsInline />
        <canvas ref={canvasRef} hidden />
        {visibleCameraState !== "live" ? (
          <div className="cameraOverlay">
            <strong>{visibleCameraState === "blocked" ? "Camera blocked" : "Camera idle"}</strong>
            <span>{visibleCameraState === "starting" ? "Starting camera" : "Preview paused"}</span>
          </div>
        ) : null}
      </div>
    </section>
  );
}
