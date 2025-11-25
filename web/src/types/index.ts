export interface DisposalGuidance {
  bin: string;
  action: string;
  description: string;
  icon: string;
  color: string;
}

export interface Detection {
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  bbox_pixels: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  class: string;
  class_group: string;
  class_original?: string;
  confidence: number;
  guidance?: DisposalGuidance;
}

export interface GroupSummaryItem {
  count: number;
  guidance: DisposalGuidance;
}

export interface DetectionResponse {
  type: 'ready' | 'detections' | 'error' | 'warning';
  message?: string;
  min_confidence?: number;
  max_fps?: number;
  timestamp?: number;
  detections?: Detection[];
  count?: number;
  group_summary?: Record<string, GroupSummaryItem>;
}

export type WSStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

