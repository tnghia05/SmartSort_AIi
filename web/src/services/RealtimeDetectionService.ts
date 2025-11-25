import { WS_URL, API_ENDPOINTS } from '../config/api';
import { DetectionResponse, WSStatus } from '../types';

type MessageHandler = (data: DetectionResponse) => void;
type StatusHandler = (status: WSStatus) => void;

export class RealtimeDetectionService {
  private ws: WebSocket | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private statusHandlers: Set<StatusHandler> = new Set();
  private status: WSStatus = 'disconnected';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private frameInterval: number | null = null;
  private maxFps = 5;

  constructor() {
    // Don't connect immediately - wait for user to start camera
    // this.connect();
    console.log('RealtimeDetectionService created (not connected yet)');
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.setStatus('connecting');
    const wsUrl = `${WS_URL}${API_ENDPOINTS.WS_DETECT}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.setStatus('connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data: DetectionResponse = JSON.parse(event.data);
          
          if (data.type === 'ready') {
            console.log('✅ WebSocket ready message received:', data);
            if (data.max_fps) {
              this.maxFps = data.max_fps;
            }
          } else if (data.type === 'detections') {
            console.log(`📦 Detections received: ${data.count || 0} objects`, data.detections?.length || 0);
            if (data.detections && data.detections.length > 0) {
              console.log('Detection details:', data.detections.map(d => `${d.class} (${(d.confidence * 100).toFixed(0)}%)`));
            }
          } else if (data.type === 'error' || data.type === 'warning') {
            console.warn('WebSocket message:', data.type, data.message);
          }

          this.messageHandlers.forEach(handler => handler(data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        console.error('❌ WebSocket URL:', wsUrl);
        this.setStatus('error');
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket closed. Code:', event.code, 'Reason:', event.reason);
        console.log('🔌 WebSocket URL was:', wsUrl);
        this.setStatus('disconnected');
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.setStatus('error');
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  private setStatus(status: WSStatus) {
    this.status = status;
    this.statusHandlers.forEach(handler => handler(status));
  }

  sendFrame(base64Image: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const frameSize = base64Image.length;
      this.ws.send(JSON.stringify({
        image: base64Image,
        format: 'base64'
      }));
      console.log(`📤 Frame sent (${(frameSize / 1024).toFixed(1)}KB)`);
    } else {
      console.warn('⚠️ WebSocket not open, readyState:', this.ws?.readyState, 'status:', this.status);
    }
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.add(handler);
    return () => this.statusHandlers.delete(handler);
  }

  getStatus(): WSStatus {
    return this.status;
  }

  disconnect() {
    if (this.frameInterval) {
      clearInterval(this.frameInterval);
      this.frameInterval = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus('disconnected');
  }

  getMaxFps(): number {
    return this.maxFps;
  }
}

