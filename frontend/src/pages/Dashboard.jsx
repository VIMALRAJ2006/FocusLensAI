import { useCallback, useState } from "react";
import AttentionCard from "../components/AttentionCard";
import AttentionChart from "../components/AttentionChart";
import StatusBadge from "../components/StatusBadge";
import WebcamPanel from "../components/WebcamPanel";
import { useAttentionSocket } from "../hooks/useAttentionSocket";

function formatDuration(seconds = 0) {
  const total = Math.max(0, Math.floor(seconds));
  const mins = String(Math.floor(total / 60)).padStart(2, "0");
  const secs = String(total % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

function numberValue(value, fallback = "0") {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(1) : fallback;
}

function formatUpdatedTime(timestamp) {
  if (!timestamp) return "Waiting";
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function Dashboard() {
  const {
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
  } = useAttentionSocket();
  const [sessionActive, setSessionActive] = useState(false);

  const sessionStats = session || {};
  const lastUpdated = formatUpdatedTime(metrics?.timestamp);

  const startSession = useCallback(() => {
    setSessionActive(true);
    connect();
  }, [connect]);

  const stopSession = useCallback(() => {
    setSessionActive(false);
    disconnect();
  }, [disconnect]);

  const resetSession = useCallback(() => {
    reset();
  }, [reset]);

  const handleFrame = useCallback(
    (blob) => {
      if (sessionActive && connected) {
        sendFrame(blob);
      }
    },
    [connected, sendFrame, sessionActive],
  );

  return (
    <main className="dashboard">
      <header className="topBar">
        <div>
          <p className="eyebrow">Real-time classroom analytics</p>
          <h1>Attention dashboard</h1>
        </div>
        <div className="topActions">
          <StatusBadge value={connected ? "connected" : connecting ? "connecting" : "disconnected"} label={connected ? "Connected" : connecting ? "Connecting" : "Disconnected"} />
          <button type="button" className="primaryButton" onClick={startSession} disabled={sessionActive}>
            Start session
          </button>
          <button type="button" className="secondaryButton" onClick={stopSession} disabled={!sessionActive}>
            Stop
          </button>
          <button type="button" className="ghostButton" onClick={resetSession} disabled={!connected}>
            Reset
          </button>
        </div>
      </header>

      {error ? <div className="errorBanner">{error}</div> : null}

      <div className="dashboardGrid">
        <div className="primaryColumn">
          <WebcamPanel
            key={sessionActive ? "active-camera" : "idle-camera"}
            active={sessionActive}
            onFrame={handleFrame}
          />
          <AttentionChart history={history} />
        </div>

        <aside className="sideColumn">
          <AttentionCard
            metrics={metrics}
            connected={connected}
            connecting={connecting}
            streamFps={streamFps}
          />

          <section className="sessionPanel" aria-label="Session metrics">
            <div className="panelHeader">
              <div>
                <p className="eyebrow">Session</p>
                <h2>Live summary</h2>
              </div>
              <span>{lastUpdated}</span>
            </div>
            <div className="sessionGrid">
              <div>
                <span>Timer</span>
                <strong>{formatDuration(sessionStats.duration_sec)}</strong>
              </div>
              <div>
                <span>Frames</span>
                <strong>{sessionStats.frame_count ?? 0}</strong>
              </div>
              <div>
                <span>Average</span>
                <strong>{numberValue(sessionStats.avg_attention)}</strong>
              </div>
              <div>
                <span>Min / Max</span>
                <strong>
                  {Math.round(sessionStats.min_attention ?? 0)} / {Math.round(sessionStats.max_attention ?? 0)}
                </strong>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}
