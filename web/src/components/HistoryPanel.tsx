import { DetectionHistoryEntry } from '../hooks/useDetectionHistory';
import './HistoryPanel.css';

interface HistoryPanelProps {
  history: DetectionHistoryEntry[];
  onExportJson: () => void;
  onExportCsv: () => void;
  onClear: () => void;
}

const MAX_VISIBLE_ITEMS = 10;
const HISTORY_ROW_HEIGHT = 72;

export function HistoryPanel({ history, onExportJson, onExportCsv, onClear }: HistoryPanelProps) {
  const listStyle = {
    maxHeight: `${MAX_VISIBLE_ITEMS * HISTORY_ROW_HEIGHT}px`,
  };

  return (
    <div className="history-panel">
      <div className="history-header">
        <div>
          <h3>Lịch sử phân loại</h3>
          <p>{history.length === 0 ? 'Chưa có dữ liệu' : `Ghi nhận ${history.length} phiên gần đây`}</p>
          {history.length > MAX_VISIBLE_ITEMS && (
            <small className="history-hint">Đang hiển thị 10 mục đầu. Cuộn để xem thêm.</small>
          )}
        </div>
        <div className="history-actions">
          <button onClick={onExportJson}>Xuất JSON</button>
          <button onClick={onExportCsv}>Xuất CSV</button>
          <button onClick={onClear} className="ghost">Xóa</button>
        </div>
      </div>
      <div className="history-list" style={listStyle}>
        {history.length === 0 ? (
          <div className="history-empty">
            <p>Bắt đầu quét để lưu lại lịch sử phân loại.</p>
          </div>
        ) : (
          history.map(entry => (
            <div key={entry.id} className="history-item">
              <div className="history-meta">
                <span className="history-time">{new Date(entry.timestamp).toLocaleString()}</span>
                {entry.pointsAwarded > 0 && (
                  <span className="history-points">+{entry.pointsAwarded} điểm</span>
                )}
              </div>
              <div className="history-content">
                <div className="history-classes">
                  {entry.detections.map(det => (
                    <span key={det.class + det.bbox.x1} className="history-class">
                      {det.class}
                    </span>
                  ))}
                </div>
                <div className="history-groups">
                  {Object.entries(entry.groupSummary ?? {}).map(([group, data]) => (
                    <span key={group} className="history-group">
                      <strong>{group}</strong> ({data.count})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

