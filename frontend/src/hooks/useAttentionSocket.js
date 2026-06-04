import { useCallback, useEffect, useRef, useState } from "react";
import { AttentionWebSocket } from "../services/websocket";

const HISTORY_LIMIT = 90;

const EMPTY_SESSION = {
  frame_count: 0,
  duration_sec: 0,
  avg_attention: 0,
  min_attention: 0,
  max_attention: 0,
};

function appendHistory(history, metrics) {
  const point = {
    score: Number(metrics.attention_score ?? 0),
    state: metrics.focus_state || metrics.attention_state || "inactive",
    timestamp: metrics.timestamp || new Date().toISOString(),
  };
  return [...history.slice(-(HISTORY_LIMIT - 1)), point];
}

export function useAttentionSocket() {
  const socketRef = useRef(null);
  const lastMessageAtRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [session, setSession] = useState(EMPTY_SESSION);
  const [history, setHistory] = useState([]);
  const [streamFps, setStreamFps] = useState(0);

  useEffect(() => {
    const socket = new AttentionWebSocket();
    socketRef.current = socket;

    const unsubscribe = socket.subscribe((event) => {
      if (event.type === "connecting") {
        setConnecting(true);
        setError("");
      }
      if (event.type === "open") {
        setConnected(true);
        setConnecting(false);
        setError("");
      }
      if (event.type === "close") {
        setConnected(false);
        setConnecting(socket.shouldReconnect);
      }
      if (event.type === "error") {
        setError(event.message || "Connection error");
      }
      if (event.type === "message") {
        const data = event.data;

        if (data.event === "session_started") {
          setSession(data.session || EMPTY_SESSION);
          return;
        }

        if (data.event === "reset") {
          setSession(data.session || EMPTY_SESSION);
          setMetrics(null);
          setHistory([]);
          setStreamFps(0);
          lastMessageAtRef.current = null;
          return;
        }

        if (data.event === "session_ended") {
          setSession(data.session || EMPTY_SESSION);
          return;
        }

        if (data.attention_score !== undefined) {
          const now = performance.now();
          if (lastMessageAtRef.current) {
            const delta = now - lastMessageAtRef.current;
            if (delta > 0) {
              const nextFps = 1000 / delta;
              setStreamFps((current) =>
                current > 0 ? current * 0.82 + nextFps * 0.18 : nextFps,
              );
            }
          }
          lastMessageAtRef.current = now;

          setMetrics(data);
          setSession(data.session || EMPTY_SESSION);
          setHistory((current) => appendHistory(current, data));
        }
      }
    });

    return () => {
      unsubscribe();
      socket.disconnect();
    };
  }, []);

  const connect = useCallback(() => socketRef.current?.connect(), []);
  const disconnect = useCallback(() => socketRef.current?.disconnect(), []);
  const reset = useCallback(() => socketRef.current?.reset(), []);
  const sendFrame = useCallback((blob) => socketRef.current?.sendFrame(blob), []);

  return {
    connected,
    connecting,
    error,
    metrics,
    session,
    history,
    streamFps,
    connect,
    disconnect,
    reset,
    sendFrame,
  };
}
