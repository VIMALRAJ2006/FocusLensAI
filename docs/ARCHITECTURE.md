# FocusLens AI — Architecture

## System layers

```
Frontend (React)  →  Backend (FastAPI)  →  AI Engine (Python)
```

Each layer has a single responsibility. Business logic does not live in route files or UI layout components.

## Communication flow

```
Webcam (browser)
    ↓  JPEG frames
WebSocket /ws/attention
    ↓
FastAPI Backend
    ↓  session + coordination
AI Engine
    ↓  OpenCV decode → MediaPipe landmarks → detectors → scorer
Attention metrics (JSON)
    ↓
WebSocket stream
    ↓
React Dashboard
```

## Frontend (`frontend/`)

| Area | Role |
|------|------|
| `services/attentionSocket.js` | WebSocket client (no React) |
| `hooks/` | `useAttentionStream`, `useSession` |
| `components/webcam/` | Webcam capture and frame export |
| `components/dashboard/` | Layout and session controls |
| `components/metrics/` | Gauges, cards, session stats |
| `components/charts/` | Score history and component breakdown |
| `utils/` | Session metric helpers |

**Responsibilities:** display feed, dashboard, live score, charts, session metrics. No CV logic.

## Backend (`backend/app/`)

| Area | Role |
|------|------|
| `routes/` | Thin HTTP/WebSocket route definitions |
| `websocket/` | WebSocket protocol handling |
| `services/session_service.py` | Session lifecycle and aggregates |
| `services/attention_service.py` | AI engine coordination per session |
| `ai_bridge.py` | Adapter into `ai-engine` |

**Responsibilities:** WebSocket streaming, API endpoints, session management, AI coordination. Routes delegate to services/handlers.

## AI Engine (`ai-engine/focuslens/`)

| Module | Role |
|--------|------|
| `detectors/face.py` | Face presence |
| `detectors/eyes.py` | Eye tracking |
| `detectors/drowsiness.py` | Drowsiness detection |
| `detectors/head_pose.py` | Head pose estimation |
| `ai_engine/detectors/face_mesh_detector.py` | MediaPipe Face Landmarker |
| `ai_engine/models/landmark_models.py` | Typed landmark results |
| `ai_engine/rendering/face_mesh_renderer.py` | Landmark overlay (no CV logic) |
| `ai_engine/tracking/eye_tracker.py` | Eye tracking from mesh landmarks |
| `ai_engine/metrics/eye_metrics.py` | EAR and gaze utilities |
| `ai_engine/rendering/eye_renderer.py` | EAR overlay (no CV logic) |
| `ai_engine/detection/drowsiness_detector.py` | Prolonged closure vs blinks |
| `ai_engine/config/thresholds.py` | Configurable EAR / drowsiness thresholds |
| `ai_engine/rendering/drowsiness_renderer.py` | Drowsiness overlay (no CV logic) |
| `ai_engine/pose/head_pose_estimator.py` | solvePnP head pose from mesh |
| `ai_engine/config/pose_thresholds.py` | Focus / direction angle thresholds |
| `ai_engine/rendering/head_pose_renderer.py` | Pose overlay (no CV logic) |
| `scoring/attention.py` | Attention scoring |
| `pipeline.py` | OpenCV + MediaPipe orchestration |

**Responsibilities:** all computer vision and scoring. No HTTP or UI code.

## Architecture rules

1. **Modular design** — one concern per file/module.
2. **No business logic in routes** — routes wire handlers only.
3. **Separate detection and rendering** — CV in `ai-engine`, display in `frontend`.
4. **Decoupled frontend/backend** — JSON over WebSocket only.
5. **Avoid giant files** — split charts, metrics, services, and handlers.
