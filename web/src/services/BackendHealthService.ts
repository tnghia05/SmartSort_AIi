import { API_URL, API_ENDPOINTS } from '../config/api';

export type BackendStatus = 'checking' | 'connected' | 'disconnected' | 'error';

type StatusHandler = (status: BackendStatus) => void;

export class BackendHealthService {
  private statusHandlers: Set<StatusHandler> = new Set();
  private status: BackendStatus = 'checking';
  private checkInterval: number | null = null;
  private checkIntervalMs = 5000; // Check every 5 seconds

  constructor() {
    this.checkHealth();
    this.startPeriodicCheck();
  }

  private async checkHealth() {
    const healthUrl = `${API_URL}${API_ENDPOINTS.HEALTH}`;
    try {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // Increase timeout for ngrok

      console.log('🔍 Checking backend health at:', healthUrl);
      console.log('🔍 API_URL:', API_URL);
      console.log('🔍 Health endpoint:', API_ENDPOINTS.HEALTH);
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Add ngrok-skip-browser-warning header if using ngrok
      if (API_URL.includes('ngrok')) {
        headers['ngrok-skip-browser-warning'] = 'true';
        console.log('🔧 Added ngrok-skip-browser-warning header');
      }
      
      const response = await fetch(healthUrl, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Check if response is HTML (ngrok warning page or error page)
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        const text = await response.text();
        if (text.includes('<!doctype') || text.includes('<html')) {
          console.warn('Backend health check received HTML instead of JSON. URL might be wrong or backend not accessible.');
          this.setStatus('disconnected');
          return false;
        }
      }

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'ok' && data.model_loaded) {
          this.setStatus('connected');
          return true;
        } else {
          this.setStatus('error');
          return false;
        }
      } else {
        this.setStatus('disconnected');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Backend health check failed:', errorMessage);
      console.error('❌ Error details:', error);
      
      // Check for specific error types
      if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
        console.error('💡 Possible causes:');
        console.error('  1. Backend is not running');
        console.error('  2. Backend URL is incorrect:', healthUrl);
        console.error('  3. CORS issue (check backend CORS settings)');
        console.error('  4. Mixed Content (HTTPS frontend calling HTTP backend)');
      }
      
      this.setStatus('disconnected');
      return false;
    }
  }

  private startPeriodicCheck() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    this.checkInterval = window.setInterval(() => {
      this.checkHealth();
    }, this.checkIntervalMs);
  }

  private setStatus(status: BackendStatus) {
    if (this.status !== status) {
      this.status = status;
      this.statusHandlers.forEach(handler => handler(status));
    }
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.add(handler);
    // Call immediately with current status
    handler(this.status);
    return () => this.statusHandlers.delete(handler);
  }

  getStatus(): BackendStatus {
    return this.status;
  }

  async checkNow(): Promise<boolean> {
    this.setStatus('checking');
    return await this.checkHealth();
  }

  destroy() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    this.statusHandlers.clear();
  }
}

