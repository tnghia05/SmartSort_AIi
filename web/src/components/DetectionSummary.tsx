import { Detection, GroupSummaryItem } from '../types';
import { formatDetectionName, formatMaterialName, getMaterialFromClassName } from '../utils/detectionLabels';
import './DetectionSummary.css';

interface DetectionSummaryProps {
  detections: Detection[];
  groupSummary?: Record<string, GroupSummaryItem>;
  variant?: 'default' | 'embedded';
}

export function DetectionSummary({ detections, groupSummary = {}, variant = 'default' }: DetectionSummaryProps) {
  if (detections.length === 0) {
    return (
      <div className={`detection-summary empty ${variant}`}>
        <p>Chưa phát hiện vật thể nào</p>
      </div>
    );
  }

  // Group by class_group
  const grouped = detections.reduce((acc, det) => {
    const group = det.class_group || 'unknown';
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(det);
    return acc;
  }, {} as Record<string, Detection[]>);

  const groupLabels: Record<string, string> = {
    'organic': 'Hữu cơ',
    'recyclable': 'Tái chế',
    'reusable': 'Tái sử dụng',
    'hazardous': 'Nguy hại',
    'residual': 'Rác thải',
  };

  // Count unique classes
  const uniqueClasses = new Set(detections.map(d => d.class));
  const classCounts = detections.reduce((acc, det) => {
    acc[det.class] = (acc[det.class] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className={`detection-summary ${variant}`}>
      <h3>
        Tổng kết: {detections.length} {detections.length === 1 ? 'vật thể' : 'vật thể'} 
        {uniqueClasses.size > 0 && ` (${uniqueClasses.size} loại khác nhau)`}
      </h3>
      <div className="summary-groups">
        {Object.entries(grouped).map(([group, items]) => (
          <div key={group} className="summary-group">
            <span className="group-label">{groupLabels[group] || group}:</span>
            <span className="group-count">{items.length}</span>
          </div>
        ))}
      </div>
      {Object.keys(groupSummary).length > 0 && (
        <div className="guidance-grid">
          {Object.entries(groupSummary).map(([group, summary]) => (
            <div key={group} className="guidance-card" style={{ borderColor: summary.guidance.color }}>
              <div className="guidance-icon" style={{ background: summary.guidance.color }}>
                {summary.guidance.icon}
              </div>
              <div>
                <p className="guidance-bin">{summary.guidance.bin}</p>
                <p className="guidance-action">{summary.guidance.action}</p>
                <small>{summary.guidance.description}</small>
                <div className="guidance-objects">
                  {grouped[group]?.map((det, idx) => (
                    <span key={`${det.class}-${idx}`} className="guidance-pill">
                      {formatDetectionName(det.class)}
                    </span>
                  ))}
                </div>
              </div>
              <span className="guidance-count">x{summary.count}</span>
            </div>
          ))}
        </div>
      )}
      <div className="summary-items">
        {detections.map((det, index) => {
          const count = classCounts[det.class] || 1;
          return (
            <div key={index} className="summary-item">
              <span className="item-class">
                {formatDetectionName(det.class)}
                {count > 1 && ` (x${count})`}
              </span>
              <span className="item-confidence">{(det.confidence * 100).toFixed(0)}%</span>
              { (det.material || getMaterialFromClassName(det.class)) && (
                <span className="item-material">
                  Chất liệu: {formatMaterialName(det.material || getMaterialFromClassName(det.class))}
                </span>
              )}
              {det.guidance && (
                <div className="item-guidance">
                  <span className="item-bin">{det.guidance.bin}</span>
                  <small>{det.guidance.action}</small>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

