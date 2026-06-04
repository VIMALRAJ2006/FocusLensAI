# Task 02 — Eye Tracking Module

## Status: implemented

## Output structure

```
ai-engine/ai_engine/
├── tracking/
│   └── eye_tracker.py
├── metrics/
│   └── eye_metrics.py
├── models/
│   └── eye_models.py
├── rendering/
│   └── eye_renderer.py
└── scripts/
    └── run_eye_tracking_demo.py
```

## Acceptance

- [x] Reuses face mesh landmarks (no duplicate MediaPipe session)
- [x] Left/right eye extraction and EAR calculation
- [x] Eye open/closed state from EAR threshold
- [x] Live EAR display in demo
- [x] Metrics, tracking, and rendering separated
- [x] Typed `EyeTrackingResult` / `EyePoint`
- [x] Gaze helpers extensible in `eye_metrics.estimate_gaze`
- [x] `AttentionPipeline` preserved via `EyeTracker.track(mesh)`

## Run demo

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_eye_tracking_demo.py
```

Press **Q** to exit.
