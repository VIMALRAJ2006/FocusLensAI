import StatusBadge from "./StatusBadge";

function formatState(value) {
  if (!value) return "Inactive";
  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function clampScore(score) {
  return Math.max(0, Math.min(100, Number(score || 0)));
}

export default function AttentionCard({ metrics, connected, connecting, streamFps }) {
  const score = clampScore(metrics?.attention_score);
  const focusState = metrics?.focus_state || metrics?.attention_state || "inactive";
  const drowsiness = metrics
    ? metrics.drowsiness_state || (metrics.drowsy ? "drowsy" : "alert")
    : "inactive";
  const headDirection = metrics?.head_direction || "unknown";
  const connectionState = connected ? "connected" : connecting ? "connecting" : "disconnected";
  const gazeLabel = metrics ? (metrics.gaze_forward ? "Forward" : "Away") : "Unknown";
  const postureLabel = metrics ? (metrics.head_upright ? "Upright" : "Off center") : "Unknown";

  return (
    <section className="attentionCard" aria-label="Attention summary">
      <div className="summaryHeader">
        <div>
          <p className="eyebrow">Live score</p>
          <h1>FocusLens AI</h1>
        </div>
        <StatusBadge value={connectionState} label={formatState(connectionState)} />
      </div>

      <div className="scoreRow">
        <div
          className="scoreRing"
          style={{ "--score": `${score * 3.6}deg` }}
          aria-label={`Attention score ${Math.round(score)}`}
        >
          <div>
            <strong>{Math.round(score)}</strong>
            <span>/100</span>
          </div>
        </div>

        <div className="statusStack">
          <div>
            <span className="metricLabel">Focus state</span>
            <StatusBadge value={focusState} label={formatState(focusState)} />
          </div>
          <div>
            <span className="metricLabel">Drowsiness</span>
            <StatusBadge value={drowsiness} label={formatState(drowsiness)} />
          </div>
        </div>
      </div>

      <div className="metricGrid">
        <div className="metricTile">
          <span>Head</span>
          <strong>{formatState(headDirection)}</strong>
        </div>
        <div className="metricTile">
          <span>Stream</span>
          <strong>{streamFps ? `${streamFps.toFixed(1)} FPS` : "0.0 FPS"}</strong>
        </div>
        <div className="metricTile">
          <span>Gaze</span>
          <strong>{gazeLabel}</strong>
        </div>
        <div className="metricTile">
          <span>Posture</span>
          <strong>{postureLabel}</strong>
        </div>
      </div>
    </section>
  );
}
