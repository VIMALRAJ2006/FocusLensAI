# FocusLens AI — Architecture Specification

## System Architecture

Frontend → Backend → AI Engine

---

## Frontend Responsibilities

Framework:
- React.js

Responsibilities:
- Display webcam feed
- Show analytics dashboard
- Display live attention score
- Render graphs and charts
- Show session metrics

---

## Backend Responsibilities

Framework:
- FastAPI

Responsibilities:
- WebSocket communication
- API endpoints
- Attention data streaming
- Session management
- AI engine coordination

---

## AI Engine Responsibilities

Language:
- Python

Modules:
- Face detection
- Eye tracking
- Drowsiness detection
- Head pose estimation
- Attention scoring

---

## Communication Flow

Webcam
↓
OpenCV Frame Capture
↓
MediaPipe Processing
↓
Attention Analysis
↓
FastAPI Backend
↓
WebSocket Streaming
↓
React Dashboard

---

## Architecture Rules

- Maintain modular design
- Avoid business logic in route files
- Separate detection and rendering logic
- Keep frontend/backend decoupled
- Avoid giant files