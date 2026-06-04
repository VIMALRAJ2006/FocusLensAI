const STATUS_STYLES = {
  focused: "statusBadge focused",
  distracted: "statusBadge distracted",
  drowsy: "statusBadge drowsy",
  inactive: "statusBadge inactive",
  alert: "statusBadge focused",
  connected: "statusBadge focused",
  connecting: "statusBadge pending",
  disconnected: "statusBadge inactive",
};

export default function StatusBadge({ value, label }) {
  const normalized = String(value || "inactive").toLowerCase();
  const className = STATUS_STYLES[normalized] || "statusBadge pending";

  return <span className={className}>{label || normalized}</span>;
}
