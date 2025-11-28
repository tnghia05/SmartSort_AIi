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

const BOX_SHRINK_RATIO = 0.06;
const BOX_SHRINK_MAX = 0.08;
const BOX_SHRINK_MIN = 0.01;
const BOX_SHRINK_PIXEL_BUFFER = 0.005; // ~0.5%

function shrinkBBox(bbox: Detection['bbox']) {
  const width = bbox.x2 - bbox.x1;
  const height = bbox.y2 - bbox.y1;
  if (width <= 0 || height <= 0) {
    return bbox;
  }
  let shrinkX = Math.min(Math.max(width * BOX_SHRINK_RATIO, BOX_SHRINK_MIN), BOX_SHRINK_MAX);
  let shrinkY = Math.min(Math.max(height * BOX_SHRINK_RATIO, BOX_SHRINK_MIN), BOX_SHRINK_MAX);

  shrinkX = Math.max(shrinkX, BOX_SHRINK_PIXEL_BUFFER);
  shrinkY = Math.max(shrinkY, BOX_SHRINK_PIXEL_BUFFER);

  if (width <= shrinkX * 2) {
    shrinkX = width * 0.1;
  }
  if (height <= shrinkY * 2) {
    shrinkY = height * 0.1;
  }

  const next = {
    x1: Math.max(0, Math.min(1, bbox.x1 + shrinkX)),
    y1: Math.max(0, Math.min(1, bbox.y1 + shrinkY)),
    x2: Math.max(0, Math.min(1, bbox.x2 - shrinkX)),
    y2: Math.max(0, Math.min(1, bbox.y2 - shrinkY)),
  };

  if (next.x2 <= next.x1 || next.y2 <= next.y1) {
    return bbox;
  }
  return next;
}

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
          const { class: className, class_group, confidence } = detection;
          const bbox = shrinkBBox(detection.bbox);
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
        const { class: className, class_group, confidence } = detection;
        const bbox = shrinkBBox(detection.bbox);
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

