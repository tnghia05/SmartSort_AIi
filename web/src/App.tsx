import { useEffect, useRef, useState } from 'react';
import { CameraView } from './components/CameraView';
import { DetectionOverlay } from './components/DetectionOverlay';
import { DetectionSummary } from './components/DetectionSummary';
import { HistoryPanel } from './components/HistoryPanel';
import { StatsCard } from './components/StatsCard';
import { RealtimeDetectionService } from './services/RealtimeDetectionService';
import { BackendHealthService } from './services/BackendHealthService';
import { RewardService, RewardEvent } from './services/RewardService';
import { useDetectionHistory } from './hooks/useDetectionHistory';
import { Detection, DetectionResponse, GroupSummaryItem, WSStatus } from './types';
import { formatDetectionName, formatMaterialName, getMaterialFromClassName } from './utils/detectionLabels';
import './App.css';

const GROUP_POINT_HINT: Record<string, number> = {
  organic: 1,
  recyclable: 2,
  reusable: 2,
  residual: 1,
  hazardous: 3,
};

function App() {
  console.log('App component rendering...');
  const [detections, setDetections] = useState<Detection[]>([]);
  const [groupSummary, setGroupSummary] = useState<Record<string, GroupSummaryItem>>({});
  const [wsStatus, setWsStatus] = useState<WSStatus>('disconnected');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected' | 'error'>('checking');
  const [videoSize, setVideoSize] = useState({ width: 1280, height: 720 }); // Default size
  const [error, setError] = useState<string | null>(null);
  const [initError, setInitError] = useState<string | null>(null);
  const [points, setPoints] = useState(0);
  const [rewardEvents, setRewardEvents] = useState<RewardEvent[]>([]);
  const [rewardModalOpen, setRewardModalOpen] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [lastScanDetections, setLastScanDetections] = useState<Detection[]>([]);
  const [lastScanPoints, setLastScanPoints] = useState(0);
  const [lastScanGroupSummary, setLastScanGroupSummary] = useState<Record<string, GroupSummaryItem>>({});
  const detectionServiceRef = useRef<RealtimeDetectionService | null>(null);
  const backendHealthRef = useRef<BackendHealthService | null>(null);
  const rewardServiceRef = useRef<RewardService | null>(null);
  const { history, addEntry, clearHistory, exportJson, exportCsv } = useDetectionHistory();

  useEffect(() => {
    rewardServiceRef.current = new RewardService();
    setPoints(rewardServiceRef.current.getPoints());
    setRewardEvents(rewardServiceRef.current.getEvents());
  }, []);

  useEffect(() => {
    console.log('App useEffect running...');
    let mounted = true;
    
    try {
      // Initialize Backend Health Service
      console.log('Creating BackendHealthService...');
      const healthService = new BackendHealthService();
      backendHealthRef.current = healthService;
      
      const unsubscribeHealth = healthService.onStatus((status) => {
        if (mounted) {
          setBackendStatus(status);
          console.log('Backend status:', status);
        }
      });
      
      // Initialize WebSocket service (but don't connect yet)
      console.log('Creating RealtimeDetectionService...');
      const service = new RealtimeDetectionService();
      console.log('RealtimeDetectionService created');
      
      if (!mounted) return;
      
      detectionServiceRef.current = service;
      console.log('Detection service initialized');

      // Listen to status changes
      const unsubscribeStatus = service.onStatus((status) => {
        console.log('WebSocket status changed:', status);
        setWsStatus(status);
      });

      // Listen to detection messages
      const unsubscribeMessage = service.onMessage((data: DetectionResponse) => {
        if (data.type === 'detections') {
          console.log('📊 App received detections:', data.count || 0, 'objects');
          if (data.detections) {
            setDetections(data.detections);
            console.log('✅ Updated detections state:', data.detections.length);
            setGroupSummary(data.group_summary || {});
            if (data.detections.length > 0) {
              setLastScanDetections(data.detections);
              setLastScanGroupSummary(data.group_summary || {});
            }
            if (rewardServiceRef.current && data.detections.length > 0) {
              const rewardResult = rewardServiceRef.current.awardForDetections(data.detections);
              if (rewardResult.addedPoints > 0) {
                setPoints(rewardResult.totalPoints);
                setRewardEvents(rewardServiceRef.current.getEvents());
                setLastScanPoints(rewardResult.addedPoints);
              } else {
                setLastScanPoints(0);
              }
              const signature = data.detections
                .map(det => `${det.class}-${det.class_group}`)
                .sort()
                .join('|');
              if (signature) {
                addEntry({
                  id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
                  timestamp: Date.now(),
                  detections: data.detections,
                  groupSummary: data.group_summary,
                  pointsAwarded: rewardResult.addedPoints,
                  signature
                });
              }
            }
          } else {
            setDetections([]);
            console.log('⚠️ No detections in response');
            setGroupSummary({});
          }
        } else if (data.type === 'ready') {
          console.log('✅ WebSocket ready, min_confidence:', data.min_confidence, 'max_fps:', data.max_fps);
        } else if (data.type === 'error') {
          console.error('❌ Detection error:', data.message);
        } else if (data.type === 'warning') {
          console.warn('⚠️ Detection warning:', data.message);
        }
      });

      return () => {
        console.log('App useEffect cleanup');
        mounted = false;
        unsubscribeStatus();
        unsubscribeMessage();
        unsubscribeHealth();
        service.disconnect();
        if (healthService) {
          healthService.destroy();
        }
      };
    } catch (err) {
      console.error('Error initializing detection service:', err);
      const errMsg = err instanceof Error ? err.message : String(err);
      if (mounted) {
        setWsStatus('error');
        setError(errMsg);
        setInitError(errMsg);
      }
    }
  }, [addEntry]);

  // Show error if initialization failed
  if (initError) {
  return (
      <div style={{ padding: '20px', minHeight: '100vh', background: '#fff' }}>
        <h1 style={{ color: '#333' }}>SmartSort AI</h1>
        <div style={{ padding: '20px', background: '#ffebee', border: '1px solid #f44336', borderRadius: '8px', marginTop: '20px' }}>
          <h2 style={{ color: '#c62828' }}>Lỗi khởi tạo ứng dụng</h2>
          <p style={{ color: '#c62828' }}>{initError}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{ 
              padding: '10px 20px', 
              background: '#f44336', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Tải lại trang
          </button>
        </div>
      </div>
    );
  }

  const handleFrame = (base64: string) => {
    if (!detectionServiceRef.current) {
      return;
    }

    // Check actual WebSocket status from service, not state
    const actualStatus = detectionServiceRef.current.getStatus();
    
    // Auto-connect if not connected yet
    if (actualStatus === 'disconnected' || actualStatus === 'error') {
      if (wsStatus !== 'connecting') { // Avoid multiple connection attempts
        console.log('WebSocket not connected, attempting to connect...');
        detectionServiceRef.current.connect();
      }
      return;
    }

    // Send frame if connected
    if (actualStatus === 'connected') {
      detectionServiceRef.current.sendFrame(base64);
    }
  };

  const scanState: 'idle' | 'processing' | 'result' = (() => {
    if (lastScanDetections.length > 0) {
      return 'result';
    }
    if (cameraActive && wsStatus === 'connected') {
      return 'processing';
    }
    return 'idle';
  })();


  const getStatusColor = () => {
    switch (wsStatus) {
      case 'connected':
        return '#4CAF50';
      case 'connecting':
        return '#FF9800';
      case 'error':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const getStatusText = () => {
    switch (wsStatus) {
      case 'connected':
        return 'Đã kết nối';
      case 'connecting':
        return 'Đang kết nối...';
      case 'error':
        return 'Lỗi kết nối';
      default:
        return 'Chưa kết nối';
    }
  };

  const getBackendStatusColor = () => {
    switch (backendStatus) {
      case 'connected':
        return '#4CAF50';
      case 'checking':
        return '#FF9800';
      case 'error':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const getBackendStatusText = () => {
    switch (backendStatus) {
      case 'connected':
        return 'Đã kết nối';
      case 'checking':
        return 'Đang kiểm tra...';
      case 'error':
        return 'Lỗi';
      default:
        return 'Mất kết nối';
    }
  };

  console.log('App render - error:', error, 'wsStatus:', wsStatus, 'detections:', detections.length);

  // Không cần check detectionServiceRef - render luôn
  // useEffect sẽ khởi tạo service sau

  if (error) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>SmartSort AI</h1>
        </header>
        <main className="app-main">
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <h2>Lỗi khởi tạo ứng dụng</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Tải lại trang</button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-avatar">
            <span role="img" aria-label="user">👤</span>
          </div>
          <div>
            <p className="brand-name">SmartSort AI</p>
            <small className="brand-tagline">Quét để phân loại rác</small>
          </div>
        </div>
        <div className="header-right">
          <div className="status-container">
            {/* Backend Status */}
            <div className="status-item">
              <span
                className="status-dot"
                style={{ 
                  backgroundColor: getBackendStatusColor(),
                  animation: backendStatus === 'checking' ? 'pulse 1.5s infinite' : 'none'
                }}
              />
              <div>
                <p className="status-label">Backend</p>
                <p className="status-value">{getBackendStatusText()}</p>
              </div>
            </div>
            {/* WebSocket Status */}
            <div className="status-item">
              <span
                className="status-dot"
                style={{ 
                  backgroundColor: getStatusColor()
                }}
              />
              <div>
                <p className="status-label">WebSocket</p>
                <p className="status-value">{getStatusText()}</p>
              </div>
            </div>
          </div>
          <button className="reward-badge" onClick={() => setRewardModalOpen(true)}>
            <span className="reward-icon">🌿</span>
            <div className="reward-info">
              <span>Điểm xanh</span>
              <strong>{points}</strong>
            </div>
          </button>
        </div>
      </header>

      {rewardModalOpen && (
        <div className="reward-modal">
          <div className="reward-modal-content">
            <div className="reward-modal-header">
              <div>
                <h3>Điểm xanh tích lũy</h3>
                <p>Tổng điểm hiện tại: <strong>{points}</strong></p>
              </div>
              <button onClick={() => setRewardModalOpen(false)}>Đóng</button>
            </div>
            <div className="reward-summary">
              <div className="reward-total">
                <p className="reward-total-label">Tổng điểm</p>
                <h2>{points}</h2>
                <p className="reward-total-hint">
                  +{rewardEvents[0]?.points ?? 0} điểm trong lần gần nhất
                </p>
              </div>
              <div className="reward-tip">
                <p>Quét đều đặn mỗi ngày để mở khóa phần thưởng xanh và huy hiệu cộng đồng.</p>
              </div>
            </div>
            <div className="reward-event-list">
              {rewardEvents.length === 0 ? (
                <p>Chưa có điểm nào. Hãy thử quét một vật thể!</p>
              ) : (
                rewardEvents.map(event => (
                  <div key={event.id} className="reward-event">
                    <div className="reward-event-left">
                      <div className="reward-event-icon">♻️</div>
                      <div>
                        <p className="reward-reason">{event.reason}</p>
                        <small>{new Date(event.timestamp).toLocaleString()}</small>
                      </div>
                    </div>
                    <span className="reward-points">+{event.points}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <main className="app-main">
        <div className="status-message">
          <p className="status-success">✅ App đã load thành công!</p>
          <p className="status-info">
            Status: {wsStatus} | 
            <strong className={detections.length > 0 ? 'status-detected' : 'status-no-detection'}>
              {detections.length === 0 
                ? 'Chưa phát hiện vật thể' 
                : detections.length === 1 
                  ? '1 vật thể được phát hiện' 
                  : `${detections.length} vật thể được phát hiện`}
            </strong>
          </p>
        </div>
        
        <div className="camera-section" style={{ marginBottom: '16px' }}>
          <div className="camera-wrapper" style={{ position: 'relative', width: '100%' }}>
            {(() => {
              try {
                console.log('Rendering CameraView...');
                return (
                  <CameraView 
                    onFrame={handleFrame} 
                    onVideoSizeChange={(w, h) => {
                      console.log('Video size changed:', w, h);
                      setVideoSize({ width: w, height: h });
                    }}
                    onStreamChange={(active) => {
                      setCameraActive(active);
                      if (!active) {
                        setDetections([]);
                        setGroupSummary({});
                      }
                    }}
                    overlay={
                      videoSize.width > 0 && videoSize.height > 0 ? (
                        <DetectionOverlay
                          detections={detections}
                          videoWidth={videoSize.width}
                          videoHeight={videoSize.height}
                        />
                      ) : null
                    }
                  />
                );
              } catch (err) {
                console.error('Error rendering CameraView:', err);
                return (
                  <div style={{ padding: '20px', background: '#ffebee', color: '#c62828', borderRadius: '8px' }}>
                    <h3>Lỗi CameraView</h3>
                    <p>{err instanceof Error ? err.message : String(err)}</p>
                  </div>
                );
              }
            })()}
          </div>
        </div>
        <div className="scan-card card">
          {scanState === 'processing' && (
            <div className="processing-state">
              <div className="processing-bar">
                <span className="processing-wave" />
              </div>
              <p className="processing-title">Đang xử lý...</p>
              <p className="processing-hint">Giữ thiết bị ổn định ~2 giây để hệ thống nhận diện chính xác hơn.</p>
            </div>
          )}
          {scanState === 'result' && lastScanDetections[0] && (
            <div className="result-state">
              <p className="result-label">Scan Result</p>
              <h2>{formatDetectionName(lastScanDetections[0].class)}</h2>
              {(lastScanDetections[0].material || getMaterialFromClassName(lastScanDetections[0].class)) && (
                <p className="result-material">
                  Chất liệu: {formatMaterialName(lastScanDetections[0].material || getMaterialFromClassName(lastScanDetections[0].class))}
                </p>
              )}
              <p className="result-points">
                +{lastScanPoints || GROUP_POINT_HINT[lastScanDetections[0].class_group] || 1} Điểm xanh
              </p>
              {lastScanDetections[0].guidance && (
                <p className="result-guidance">
                  {lastScanDetections[0].guidance.action}
                  {' '}
                  {lastScanDetections[0].guidance.description}
                </p>
              )}
              <div className="embedded-summary">
                <DetectionSummary detections={lastScanDetections} groupSummary={lastScanGroupSummary} variant="embedded" />
              </div>
            </div>
          )}
          {scanState === 'idle' && (
            <div className="processing-state">
              <p className="processing-title">Sẵn sàng quét</p>
              <p className="processing-hint">Nhấn “QUÉT NGAY” để bắt đầu phân loại rác cùng SmartSort AI.</p>
            </div>
          )}
        </div>
        {(scanState !== 'result') && (
          <div className="results-section" style={{ width: '100%' }}>
            {(() => {
              try {
                console.log('Rendering DetectionSummary...');
                return <DetectionSummary detections={detections} groupSummary={groupSummary} />;
              } catch (err) {
                console.error('Error rendering DetectionSummary:', err);
                return (
                  <div style={{ padding: '20px', background: '#ffebee', color: '#c62828', borderRadius: '8px' }}>
                    <h3>Lỗi DetectionSummary</h3>
                    <p>{err instanceof Error ? err.message : String(err)}</p>
                  </div>
                );
              }
            })()}
          </div>
        )}
        <StatsCard history={history} />
        <HistoryPanel
          history={history}
          onExportJson={exportJson}
          onExportCsv={exportCsv}
          onClear={clearHistory}
        />
      </main>
    </div>
  );
}

export default App;
