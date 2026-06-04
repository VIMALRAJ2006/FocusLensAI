const WIDTH = 640;
const HEIGHT = 160;
const PADDING = 12;

function buildPath(points) {
  if (!points.length) return "";
  const step = (WIDTH - PADDING * 2) / Math.max(points.length - 1, 1);
  return points
    .map((point, index) => {
      const x = PADDING + index * step;
      const y = HEIGHT - PADDING - (point.score / 100) * (HEIGHT - PADDING * 2);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
}

export default function AttentionChart({ history }) {
  const path = buildPath(history);
  const latest = history.at(-1)?.score ?? 0;

  return (
    <section className="chartPanel" aria-label="Attention trend">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Trend</p>
          <h2>Attention over time</h2>
        </div>
        <span>{Math.round(latest)}</span>
      </div>

      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Attention score history">
        {[25, 50, 75].map((level) => {
          const y = HEIGHT - PADDING - (level / 100) * (HEIGHT - PADDING * 2);
          return (
            <line
              key={level}
              x1={PADDING}
              y1={y}
              x2={WIDTH - PADDING}
              y2={y}
              className="chartGrid"
            />
          );
        })}
        {path ? <path d={path} className="chartLine" /> : null}
      </svg>
    </section>
  );
}
