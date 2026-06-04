# Task 07 — React Dashboard Frontend

## Status: implemented

## Goal

Implement a real-time React dashboard for FocusLens AI that visualizes live attention analytics streamed from the backend WebSocket server.

---

## Functional Requirements

- Connect to backend WebSocket endpoint
- Capture webcam frames in browser
- Stream JPEG frames to backend
- Receive real-time attention metrics
- Display live analytics dashboard
- Show webcam preview

---

## Dashboard Features

- Live attention score
- Focus state indicator
- Drowsiness status
- Head direction
- FPS indicator
- Session timer
- Attention trend chart

---

## UI Requirements

- Responsive modern dashboard
- Clean card-based layout
- Real-time metric updates
- Stable websocket reconnect handling
- Dark theme support

---

## Architectural Requirements

- Separate websocket logic from UI components
- Use reusable React components
- Avoid business logic inside UI rendering
- Maintain scalable frontend structure

---

## Output Structure

Implemented under the existing Vite app structure:

```
frontend/
├── src/
│   ├── components/
│   │   ├── AttentionCard.jsx
│   │   ├── AttentionChart.jsx
│   │   ├── StatusBadge.jsx
│   │   └── WebcamPanel.jsx
│   │
│   ├── hooks/
│   │   └── useAttentionSocket.js
│   │
│   ├── services/
│   │   └── websocket.js
│   │
│   ├── pages/
│   │   └── Dashboard.jsx
│   │
│   ├── App.jsx
│   │
│   └── main.jsx
```

## Implementation Notes

- `services/websocket.js` owns the backend WebSocket contract.
- `useAttentionSocket` handles connection state, reconnect behavior, metrics, session data, stream FPS, and chart history.
- `WebcamPanel` captures browser webcam frames and streams JPEG blobs.
- `Dashboard` coordinates session controls without embedding WebSocket logic.
- UI displays attention score, focus state, drowsiness, head direction, FPS, session timer, session aggregates, and a live trend chart.
- Backend contracts are preserved: binary JPEG frames in, JSON metrics/events out, text `reset` command supported.

---

## Acceptance Criteria

- [x] Frontend connects to backend websocket
- [x] Webcam frames stream correctly
- [x] Attention metrics update live
- [x] Charts update in real time
- [x] Dashboard remains responsive
- [x] Stable websocket behavior maintained
