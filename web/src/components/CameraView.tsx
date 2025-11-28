import { useEffect, useRef, useState } from 'react';
import './CameraView.css';

interface CameraViewProps {
  onFrame: (base64: string) => void;
  onError?: (error: string) => void;
  onVideoSizeChange?: (width: number, height: number) => void;
  overlay?: React.ReactNode;
  onStreamChange?: (active: boolean) => void;
}

const ROI_RATIO = 0.85;
const FRAME_INTERVAL_MS = 40; // ~25 FPS
const MOTION_SAMPLE_STEP = 16; // sample every 16 pixels per channel for diff
const MOTION_THRESHOLD = 10; // average diff (0-255 scale) to treat as motion
const HEARTBEAT_INTERVAL_MS = 1200; // always send at least once per ~1.2s

export function CameraView({ onFrame, onError, onVideoSizeChange, overlay, onStreamChange }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const frameIntervalRef = useRef<number | null>(null);
  const videoSizeRef = useRef({ width: 0, height: 0 });
  const lastFrameDataRef = useRef<Uint8ClampedArray | null>(null);
  const lastFrameTimestampRef = useRef<number>(0);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, []);

  const startStream = async () => {
    try {
      // Check if getUserMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        const isHTTPS = window.location.protocol === 'https:';
        const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        
        if (!isHTTPS && !isLocalhost) {
          const errorMsg = 'Camera chỉ hoạt động trên HTTPS hoặc localhost. Vui lòng truy cập qua https:// hoặc http://localhost:5173';
          setError(errorMsg);
          onError?.(errorMsg);
          console.error('getUserMedia not available:', {
            protocol: window.location.protocol,
            hostname: window.location.hostname,
            isHTTPS,
            isLocalhost
          });
          return;
        }
        
        const errorMsg = 'Trình duyệt không hỗ trợ camera hoặc chưa được cấp quyền';
        setError(errorMsg);
        onError?.(errorMsg);
        console.error('getUserMedia not supported');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
        onStreamChange?.(true);
        setError(null);
        
        // Wait for video metadata to load
        videoRef.current.onloadedmetadata = () => {
          if (videoRef.current) {
            const width = videoRef.current.videoWidth;
            const height = videoRef.current.videoHeight;
            videoSizeRef.current = { width, height };
            onVideoSizeChange?.(width, height);
            startFrameCapture();
          }
        };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to access camera';
      setError(errorMessage);
      onError?.(errorMessage);
      console.error('Camera error:', err);
    }
  };

  const stopStream = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsStreaming(false);
    onStreamChange?.(false);
    lastFrameDataRef.current = null;
    lastFrameTimestampRef.current = 0;
  };

  const startFrameCapture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (!video || !canvas) return;

    const shouldSendFrame = (imageData: ImageData) => {
      const now = Date.now();
      const lastSentAt = lastFrameTimestampRef.current;
      const lastFrame = lastFrameDataRef.current;

      if (!lastFrame || lastFrame.length !== imageData.data.length) {
        lastFrameDataRef.current = new Uint8ClampedArray(imageData.data);
        lastFrameTimestampRef.current = now;
        return true;
      }

      let diffSum = 0;
      let samples = 0;
      const step = MOTION_SAMPLE_STEP * 4; // RGBA
      const data = imageData.data;

      for (let i = 0; i < data.length; i += step) {
        diffSum += Math.abs(data[i] - lastFrame[i]); // chỉ xét kênh R (đủ để phát hiện)
        samples += 1;
      }

      const avgDiff = samples > 0 ? diffSum / samples : 0;
      const motionDetected = avgDiff >= MOTION_THRESHOLD;
      const heartbeatDue = now - lastSentAt >= HEARTBEAT_INTERVAL_MS;

      if (motionDetected || heartbeatDue) {
        lastFrame.set(imageData.data);
        lastFrameTimestampRef.current = now;
        return true;
      }

      return false;
    };

    const captureFrame = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Crop video frame to a centered square to match UI viewfinder
        const cropSize = Math.min(video.videoWidth, video.videoHeight);
        const cropX = (video.videoWidth - cropSize) / 2;
        const cropY = (video.videoHeight - cropSize) / 2;
        canvas.width = cropSize;
        canvas.height = cropSize;

        ctx.drawImage(
          video,
          cropX,
          cropY,
          cropSize,
          cropSize,
          0,
          0,
          cropSize,
          cropSize
        );

        // Convert to base64 JPEG (resize to max 480px for better detection sensitivity)
        // Tăng từ 320 lên 480 để phát hiện tốt hơn, phù hợp với backend imgsz=480
        const maxWidth = 480;
        const scale = Math.min(1, maxWidth / canvas.width);
        const scaledWidth = Math.floor(canvas.width * scale);
        const scaledHeight = Math.floor(canvas.height * scale);

        const scaledCanvas = document.createElement('canvas');
        scaledCanvas.width = scaledWidth;
        scaledCanvas.height = scaledHeight;
        const scaledCtx = scaledCanvas.getContext('2d');
        if (scaledCtx) {
          scaledCtx.drawImage(canvas, 0, 0, scaledWidth, scaledHeight);
          const imageData = scaledCtx.getImageData(0, 0, scaledWidth, scaledHeight);
          if (!shouldSendFrame(imageData)) {
            return;
          }
          // Quality 0.7 for balance between file size and image quality
          const base64 = scaledCanvas.toDataURL('image/jpeg', 0.7);
          const base64Data = base64.split(',')[1];
          onFrame(base64Data);
        }
      }
    };

    frameIntervalRef.current = window.setInterval(captureFrame, FRAME_INTERVAL_MS);
  };

  return (
    <div className="camera-view">
      <div className="camera-frame">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`camera-video ${isStreaming ? 'is-visible' : ''}`}
        />
        <div
          className="camera-roi"
          style={{
            width: `${ROI_RATIO * 100}%`,
            height: `${ROI_RATIO * 100}%`,
          }}
        />
        {!isStreaming && (
          <div className="camera-placeholder">
            <div className="placeholder-ring">
              <span />
            </div>
            <p>Camera Viewfinder Area</p>
          </div>
        )}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        {overlay}
      </div>

      <div className="scan-actions">
        <button
          onClick={isStreaming ? stopStream : startStream}
          className="scan-primary"
        >
          <span className="scan-icon">📷</span>
          {isStreaming ? 'TẮT CAMERA' : 'QUÉT NGAY'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>Lỗi: {error}</p>
          {error.includes('HTTPS') || error.includes('localhost') ? (
            <p className="error-hint">
              <strong>Giải pháp:</strong><br />
              - Truy cập qua <code>http://localhost:5173</code> trên máy tính<br />
              - Hoặc dùng ngrok để có HTTPS
            </p>
          ) : (
            <p className="error-hint">
              Vui lòng cho phép truy cập camera trong trình duyệt
            </p>
          )}
        </div>
      )}
    </div>
  );
}

