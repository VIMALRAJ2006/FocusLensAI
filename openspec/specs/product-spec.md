# FocusLens AI — Product Specification

## Overview

FocusLens AI is a real-time classroom attention tracking system that uses computer vision and behavioral analysis to estimate user engagement during online learning sessions.

The system analyzes:
- face presence
- eye movement
- gaze direction
- head posture
- drowsiness
- distraction patterns

and generates a live attention score with engagement analytics.

---

## Goals

- Detect face presence
- Track eye movement
- Detect drowsiness
- Estimate attention level
- Generate engagement analytics
- Display real-time dashboard

---

## Tech Stack

### AI Engine
- Python
- OpenCV
- MediaPipe
- NumPy

### Backend
- FastAPI
- WebSockets

### Frontend
- React.js
- Tailwind CSS

---

## MVP Features

1. Real-time face detection
2. Eye tracking
3. Drowsiness detection
4. Attention scoring
5. Live analytics dashboard

---

## Future Scope

- Multi-user monitoring
- Emotion detection
- Attendance tracking
- Session history
- Cloud database integration

---

## Constraints

- Real-time processing required
- Modular architecture mandatory
- Frontend and backend must remain separated
- AI logic should remain isolated