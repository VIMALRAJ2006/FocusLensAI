# Task 05 - Attention Scoring Engine

## Status: implemented

## Continuation note

Task 5 was continued from the partially implemented scorer already present in
`ai-engine/focuslens/scoring/attention.py`. The existing pipeline orchestration
was preserved.

## Output structure

```
ai-engine/
├── ai_engine/
│   ├── config/
│       └── attention_thresholds.py
│   └── scripts/
│       └── run_attention_demo.py
└── focuslens/
    ├── scoring/
    │   └── attention.py
    ├── pipeline.py
    └── types.py
```

## Technical

- Reuses Task 01-04 module outputs through `AttentionPipeline`
- Computes weighted attention components: face, eyes, gaze, posture, alertness
- Applies configurable repeated-away-gaze distraction detection
- Applies exponential moving average score smoothing
- Hard-classifies drowsy and inactive states while keeping the score stable
- Emits backend-ready `FrameMetrics.to_dict()` payloads
- Provides an isolated OpenCV webcam demo via `run_attention_demo.py`

## Classification

- `focused`: face present, not drowsy, not distracted, smoothed score above threshold
- `distracted`: repeated away gaze or smoothed score below focused threshold
- `drowsy`: sustained closure reported by the drowsiness detector
- `inactive`: no face/landmarks available

## Acceptance

- [x] Reuses existing face, eye, drowsiness, and head-pose outputs
- [x] Generates real-time 0-100 attention score
- [x] Implements stable score smoothing
- [x] Classifies focused / distracted / drowsy / inactive
- [x] Keeps thresholds configurable in `AttentionThresholds`
- [x] Keeps scoring separated from rendering
- [x] Preserves `AttentionPipeline` integration for backend/WebSocket Task 6
- [x] Includes runnable Task 05 attention demo

## Run demo

```powershell
cd e:\FocusLens-AI
.\.venv\Scripts\python ai-engine\ai_engine\scripts\run_attention_demo.py
```

Press **Q** to exit.
