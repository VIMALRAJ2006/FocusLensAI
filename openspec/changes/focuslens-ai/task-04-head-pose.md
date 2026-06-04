# Task 04 — Head Pose Estimation Module

## Status: implemented

## Output structure

```
ai-engine/ai_engine/
├── pose/
│   ├── head_pose_estimator.py
│   └── pose_math.py
├── config/
│   └── pose_thresholds.py
├── models/
│   └── pose_models.py
├── rendering/
│   └── head_pose_renderer.py
└── scripts/
    └── run_head_pose_demo.py
```

## Technical

- Reuses `FaceMeshResult` landmarks (6-point model)
- `cv2.solvePnP` + Euler angles (pitch, yaw, roll)
- `angle_normalization.py` maps supplementary angles (e.g. roll 174° → ~-6°) for focus checks
- Direction: left / right / up / down / center
- Focused vs distracted via `PoseThresholds`

## Acceptance

- [x] Head orientation updates from solvePnP
- [x] Directional look detection
- [x] Focused / distracted visible in demo
- [x] Pose / rendering / config separated
- [x] `AttentionPipeline` preserved (`head_upright`)

## Run demo

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_head_pose_demo.py
```

Press **Q** to exit.
