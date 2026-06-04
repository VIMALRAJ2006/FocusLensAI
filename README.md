# FocusLens AI

Real-time classroom attention tracking using computer vision and behavioral analysis. The system estimates engagement from face presence, eye movement, gaze direction, head posture, drowsiness, and distraction patterns, then streams a live attention score to a React dashboard.

## Architecture

```
Frontend (React)  →  Backend (FastAPI)  →  AI Engine (Python)
```

```
FocusLens-AI/
├── ai-engine/          # Face, eyes, drowsiness, head pose, scoring
├── backend/app/
│   ├── routes/         # Thin API + WebSocket routes
│   ├── services/       # Session + attention coordination
│   └── websocket/      # Stream handlers
└── frontend/src/
    ├── services/       # WebSocket client
    ├── components/     # webcam, dashboard, metrics, charts
    └── hooks/          # Session + stream state
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for layer responsibilities and communication flow.

Frames flow: **webcam → WebSocket (JPEG) → backend session → OpenCV decode → MediaPipe → attention JSON → dashboard**.

## MVP features

- Real-time face detection
- Eye tracking (EAR + iris-based gaze proxy)
- Drowsiness detection (sustained low EAR)
- Composite attention score (0–100)
- Live analytics dashboard

## Prerequisites

- Python 3.10+
- Node.js 18+

## Setup

### 1. AI engine + backend

```powershell
cd e:\FocusLens-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ai-engine\requirements.txt
pip install -r backend\requirements.txt
```

On first run, the AI engine downloads `face_landmarker.task` into `ai-engine/models/` (~3 MB).

### Task 01 — Face mesh demo (webcam + landmark overlay)

```powershell
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_face_mesh_webcam.py
```

Press **Q** to quit. Detection: `ai_engine/detectors/` · Models: `ai_engine/models/` · Rendering: `ai_engine/rendering/`.

### Task 02 — Eye tracking demo (EAR + open/closed)

```powershell
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_eye_tracking_demo.py
```

Tracking: `ai_engine/tracking/` · Metrics: `ai_engine/metrics/` · Rendering: `ai_engine/rendering/eye_renderer.py`.

### Task 03 — Drowsiness demo

```powershell
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_drowsiness_demo.py
```

Detection: `ai_engine/detection/` · Config: `ai_engine/config/thresholds.py`.

### Task 04 — Head pose demo (solvePnP)

```powershell
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_head_pose_demo.py
```

Pose: `ai_engine/pose/` · Thresholds: `ai_engine/config/pose_thresholds.py`.

### 2. Frontend

```powershell
cd frontend
npm install
```

## Run

**Terminal 1 — API**

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --app-dir backend
```

**Terminal 2 — UI**

```powershell
cd e:\FocusLens-AI\frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173), click **Start session**, and allow camera access.

Optional: set `VITE_WS_URL=ws://localhost:8000/ws/attention` in `frontend/.env` if the API runs on a different host.

## API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health check |
| `WS /ws/attention` | Binary JPEG frames in → JSON metrics out; text `reset` clears session state |

## Future scope

Multi-user monitoring, emotion detection, attendance, session history, cloud database — see product spec constraints (modular, separated frontend/backend/AI).

## License

MIT (add license file if needed for your distribution).
