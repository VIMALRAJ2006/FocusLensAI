# Task 06 — FastAPI Backend + WebSocket Integration

## Status: implemented

## Goal

Implement a FastAPI backend that streams real-time attention analytics from the AI engine using WebSockets.

---

## Functional Requirements

- Create FastAPI backend server
- Add health-check endpoint
- Add WebSocket endpoint for live metrics
- Stream real-time attention analytics
- Integrate existing attention scoring pipeline

---

## REST Endpoints

### GET /health

Returns backend health status.

### GET /attention/status

Returns latest attention metrics snapshot.

---

## WebSocket Endpoint

### /ws/attention

Streams:
- attention score
- focus state
- drowsiness state
- head direction
- timestamp

---

## Architectural Requirements

- Separate routes, websocket handlers, and services
- Keep AI engine isolated from API layer
- Avoid business logic inside routes
- Preserve existing AI pipeline
- Maintain modular backend structure

---

## Output Structure

```
backend/
├── requirements.txt
└── app/
    ├── main.py
    ├── ai_bridge.py
    ├── config.py
    ├── models/
    │   └── websocket_models.py
    ├── routes/
    │   ├── attention_routes.py
    │   ├── health.py
    │   └── websocket.py
    ├── services/
    │   ├── attention_service.py
    │   └── session_service.py
    └── websocket/
        ├── attention_socket.py
        └── attention_handler.py
```

## Implementation Notes

- `GET /health` returns service health.
- `GET /attention/status` returns active session count and the latest metrics snapshot.
- `WS /ws/attention` accepts binary JPEG frames and streams timestamped attention metrics.
- Routes stay thin and delegate to `AttentionService` / `AttentionWebSocketHandler`.
- `AIBridge` is the only backend adapter into the existing AI pipeline.
- WebSocket payloads include `attention_score`, `focus_state`, `drowsiness_state`, `head_direction`, and `timestamp`.

---

## Acceptance Criteria

- [x] FastAPI server starts correctly
- [x] WebSocket connection works
- [x] Attention metrics stream successfully
- [x] Existing AI pipeline integrates correctly
- [x] Stable real-time performance maintained
