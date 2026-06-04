# Task 01 — Face Detection Module

## Status: implemented

## Output structure

```
ai-engine/ai_engine/
├── detectors/
│   └── face_mesh_detector.py
├── models/
│   ├── landmark_models.py
│   └── model_assets.py
├── rendering/
│   ├── face_mesh_renderer.py
│   └── mesh_contours.py
└── scripts/
    └── run_face_mesh_webcam.py
```

## Acceptance

- [x] OpenCV webcam frames
- [x] MediaPipe Face Landmarker
- [x] Typed `LandmarkPoint` / `FaceMeshResult`
- [x] Detection and rendering fully separated
- [x] Face presence via `FaceMeshResult.face_present`
- [x] Pipeline uses `FaceMeshDetector` directly (no duplicate landmarker adapter)
- [x] Stable FPS (640px max width, VIDEO mode for webcam)

## Run demo

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_face_mesh_webcam.py
```

Press **Q** to exit.
