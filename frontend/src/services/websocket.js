const DEFAULT_WS_URL = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:8000/ws/attention`;

export const ATTENTION_WS_URL = import.meta.env.VITE_WS_URL || DEFAULT_WS_URL;

export class AttentionWebSocket {
  constructor(url = ATTENTION_WS_URL, { reconnectDelayMs = 1200 } = {}) {
    this.url = url;
    this.reconnectDelayMs = reconnectDelayMs;
    this.socket = null;
    this.listeners = new Set();
    this.shouldReconnect = false;
    this.reconnectTimer = null;
  }

  connect() {
    if (
      this.socket?.readyState === WebSocket.OPEN ||
      this.socket?.readyState === WebSocket.CONNECTING
    ) {
      return;
    }

    this.shouldReconnect = true;
    this._clearReconnectTimer();
    this._emit({ type: "connecting" });

    const socket = new WebSocket(this.url);
    socket.binaryType = "arraybuffer";
    this.socket = socket;

    socket.onopen = () => this._emit({ type: "open" });
    socket.onerror = () => this._emit({ type: "error", message: "WebSocket error" });
    socket.onclose = () => {
      this.socket = null;
      this._emit({ type: "close" });
      if (this.shouldReconnect) {
        this.reconnectTimer = window.setTimeout(
          () => this.connect(),
          this.reconnectDelayMs,
        );
      }
    };
    socket.onmessage = (event) => {
      try {
        this._emit({ type: "message", data: JSON.parse(event.data) });
      } catch {
        this._emit({ type: "error", message: "Malformed WebSocket payload" });
      }
    };
  }

  disconnect() {
    this.shouldReconnect = false;
    this._clearReconnectTimer();
    this.socket?.close();
    this.socket = null;
  }

  sendFrame(jpegBlob) {
    if (!jpegBlob || this.socket?.readyState !== WebSocket.OPEN) {
      return false;
    }

    jpegBlob.arrayBuffer().then((buffer) => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(buffer);
      }
    });
    return true;
  }

  reset() {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send("reset");
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  _emit(event) {
    this.listeners.forEach((listener) => listener(event));
  }

  _clearReconnectTimer() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
