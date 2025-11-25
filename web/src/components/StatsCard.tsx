import { DetectionHistoryEntry } from '../hooks/useDetectionHistory';
import './StatsCard.css';

interface StatsCardProps {
  history: DetectionHistoryEntry[];
}

const GROUP_META: Record<string, { label: string; color: string }> = {
  recyclable: { label: 'Tái chế', color: '#43a047' },
  organic: { label: 'Hữu cơ', color: '#ef6c00' },
  residual: { label: 'Rác thường', color: '#546e7a' },
  hazardous: { label: 'Nguy hại', color: '#c62828' },
  reusable: { label: 'Tái sử dụng', color: '#8e24aa' },
};

export function StatsCard({ history }: StatsCardProps) {
  if (history.length === 0) {
    return (
      <div className="stats-card card">
        <p className="stats-label">Thống kê tuần này</p>
        <h3>Chưa có số liệu</h3>
        <p className="stats-empty">Hãy quét vài vật thể để SmartSort AI thống kê cho bạn.</p>
      </div>
    );
  }

  const aggregated: Record<string, number> = {};
  history.slice(0, 20).forEach(entry => {
    Object.entries(entry.groupSummary ?? {}).forEach(([group, data]) => {
      aggregated[group] = (aggregated[group] || 0) + data.count;
    });
  });

  const total = Object.values(aggregated).reduce((sum, val) => sum + val, 0) || 1;
  const chartData = Object.entries(GROUP_META).map(([group, meta]) => ({
    group,
    label: meta.label,
    color: meta.color,
    percent: Math.round(((aggregated[group] || 0) / total) * 100),
  }));
  const recent = history.slice(0, 3);

  return (
    <div className="stats-card card">
      <div className="stats-header">
        <div>
          <p className="stats-label">Thống kê tuần này</p>
          <h3>Hoạt động quét</h3>
        </div>
        <span className="stats-total">{total} vật thể</span>
      </div>

      <div className="stats-chart">
        {chartData.map(item => (
          <div key={item.group} className="stats-bar">
            <div className="stats-bar-label">
              <span style={{ background: item.color }} />
              {item.label}
            </div>
            <div className="stats-bar-track">
              <div
                className="stats-bar-fill"
                style={{ width: `${item.percent}%`, background: item.color }}
              />
            </div>
            <span className="stats-bar-value">{item.percent}%</span>
          </div>
        ))}
      </div>

      <div className="stats-history">
        <p className="stats-label">Lịch sử quét gần đây</p>
        {recent.map(entry => {
          const firstDet = entry.detections[0];
          return (
            <div key={entry.id} className="stats-history-item">
              <div className="stats-history-icon">🗑️</div>
              <div>
                <p className="stats-history-title">{firstDet?.class || 'Vật thể'}</p>
                <small>{new Date(entry.timestamp).toLocaleString()}</small>
              </div>
              {entry.pointsAwarded > 0 && (
                <span className="stats-history-points">+{entry.pointsAwarded}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

