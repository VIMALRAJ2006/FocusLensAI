# Task 03 — Drowsiness Detection Module

## Status: implemented

## Output structure

```
ai-engine/ai_engine/
├── detection/
│   └── drowsiness_detector.py
├── config/
│   └── thresholds.py
├── models/
│   └── drowsiness_models.py
├── rendering/
│   └── drowsiness_renderer.py
└── scripts/
    └── run_drowsiness_demo.py
```

## Detection rules

- Reuses `EyeTrackingResult` / EAR from Task 02
- **Blink:** closure ≤ `blink_max_closed_frames` (default 5)
- **Drowsy:** consecutive closed frames ≥ `drowsiness_min_consecutive_frames` (default 12)
- **Reset:** drowsy state clears when eyes reopen
- Thresholds in `DrowsinessThresholds` (no magic numbers in detector)

## Acceptance

- [x] Drowsiness state updates correctly
- [x] Blinks do not latch drowsy (short closure + reopen resets)
- [x] Prolonged closure triggers drowsy
- [x] Detection / config / rendering separated
- [x] `AttentionPipeline` preserved

## Run demo

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_drowsiness_demo.py
```

Press **Q** to exit. Hold eyes closed ~2s to trigger **DROWSY**; quick blinks show **BLINK**.
