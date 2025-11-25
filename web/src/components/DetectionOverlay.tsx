import { useEffect, useRef, useState } from 'react';
import { Detection } from '../types';
import './DetectionOverlay.css';

interface DetectionOverlayProps {
  detections: Detection[];
  videoWidth: number;
  videoHeight: number;
}

const CLASS_COLORS: Record<string, string> = {
  'organic': '#4CAF50',
  'recyclable': '#2196F3',
  'reusable': '#FF9800',
  'hazardous': '#F44336',
  'residual': '#9E9E9E',
};

export function DetectionOverlay({ detections, videoWidth, videoHeight }: DetectionOverlayProps) {
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Get container from parent (camera-container)
    const container = overlayRef.current?.parentElement;
    if (!container) {
      console.warn('DetectionOverlay: No parent container found');
      return;
    }

    const updateSize = () => {
      const rect = container.getBoundingClientRect();
      console.log('DetectionOverlay: Container size updated', rect.width, rect.height);
      setContainerSize({ width: rect.width, height: rect.height });
    };

    // Try to update immediately
    updateSize();
    
    // Also use a small delay to ensure container is rendered
    const timeoutId = setTimeout(updateSize, 100);
    
    const resizeObserver = new ResizeObserver(updateSize);
    resizeObserver.observe(container);

    return () => {
      clearTimeout(timeoutId);
      resizeObserver.disconnect();
    };
  }, []);

  // Debug log
  useEffect(() => {
    console.log('DetectionOverlay render check:', {
      videoWidth,
      videoHeight,
      detectionsCount: detections.length,
      containerSize
    });
  }, [videoWidth, videoHeight, detections.length, containerSize]);

  if (!videoWidth || !videoHeight || detections.length === 0) {
    return null;
  }

  // If container size is not ready, use a fallback
  if (!containerSize.width || !containerSize.height) {
    console.warn('DetectionOverlay: Container size not ready, using fallback');
    // Return overlay anyway but with simplified positioning
    return (
      <div ref={overlayRef} className="detection-overlay">
        {detections.map((detection, index) => {
          const { bbox, class: className, class_group, confidence } = detection;
          const color = CLASS_COLORS[class_group] || '#9E9E9E';
          
          const style: React.CSSProperties = {
            position: 'absolute',
            left: `${bbox.x1 * 100}%`,
            top: `${bbox.y1 * 100}%`,
            width: `${(bbox.x2 - bbox.x1) * 100}%`,
            height: `${(bbox.y2 - bbox.y1) * 100}%`,
            border: `2px solid ${color}`,
            borderRadius: '4px',
            pointerEvents: 'none',
          };

          const isMobile = window.innerWidth <= 768;
          const labelStyle: React.CSSProperties = {
            position: 'absolute',
            top: isMobile ? '-20px' : '-24px',
            left: '0',
            background: color,
            color: 'white',
            padding: isMobile ? '2px 6px' : '2px 8px',
            borderRadius: '4px',
            fontSize: isMobile ? '10px' : '12px',
            fontWeight: '600',
            whiteSpace: 'nowrap',
            maxWidth: '90%',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            // No transform needed - box coordinates are already mirrored
          };

          return (
            <div key={index} style={style}>
              <div style={labelStyle}>
                {className} ({(confidence * 100).toFixed(0)}%)
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Use normalized bbox (0-1) directly as percentages
  // Video is not mirrored, so use bbox coordinates directly
  
  return (
    <div ref={overlayRef} className="detection-overlay">
      {detections.map((detection, index) => {
        const { bbox, class: className, class_group, confidence } = detection;
        const color = CLASS_COLORS[class_group] || '#9E9E9E';
        
        // Use normalized bbox (0-1) directly as percentages
        // No mirroring needed - video displays normally
        const style: React.CSSProperties = {
          position: 'absolute',
          left: `${bbox.x1 * 100}%`,
          top: `${bbox.y1 * 100}%`,
          width: `${(bbox.x2 - bbox.x1) * 100}%`,
          height: `${(bbox.y2 - bbox.y1) * 100}%`,
          border: `2px solid ${color}`,
          borderRadius: '4px',
          pointerEvents: 'none',
        };

        // Label position: place on top-left of box
        const isMobile = window.innerWidth <= 768;
        const labelStyle: React.CSSProperties = {
          position: 'absolute',
          top: isMobile ? '-20px' : '-24px',
          left: '0',
          background: color,
          color: 'white',
          padding: isMobile ? '2px 6px' : '2px 8px',
          borderRadius: '4px',
          fontSize: isMobile ? '10px' : '12px',
          fontWeight: '600',
          whiteSpace: 'nowrap',
          maxWidth: '90%',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        };

        return (
          <div key={index} style={style}>
            <div style={labelStyle}>
              {className} ({(confidence * 100).toFixed(0)}%)
            </div>
          </div>
        );
      })}
    </div>
  );
}

