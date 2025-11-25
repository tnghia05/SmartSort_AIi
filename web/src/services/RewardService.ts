import { Detection } from '../types';

export interface RewardEvent {
  id: string;
  timestamp: number;
  points: number;
  className: string;
  group: string;
  reason: string;
}

export interface RewardResult {
  addedPoints: number;
  totalPoints: number;
  events: RewardEvent[];
}

const POINTS_KEY = 'smartsort:rewards:points';
const EVENTS_KEY = 'smartsort:rewards:events';
const RECENT_KEY = 'smartsort:rewards:recent';

const GROUP_POINTS: Record<string, number> = {
  organic: 1,
  recyclable: 2,
  reusable: 2,
  residual: 1,
  hazardous: 3,
};

const DEFAULT_COOLDOWN_MS = 15000;

export class RewardService {
  private points = 0;
  private events: RewardEvent[] = [];
  private recentMap: Map<string, number> = new Map();
  private cooldownMs = DEFAULT_COOLDOWN_MS;

  constructor() {
    this.points = this.readNumber(POINTS_KEY) ?? 0;
    this.events = this.readJson<RewardEvent[]>(EVENTS_KEY, []) ?? [];
    const recent = this.readJson<[string, number][]>(RECENT_KEY, []);
    if (recent) {
      this.recentMap = new Map(recent);
    }
  }

  getPoints() {
    return this.points;
  }

  getEvents() {
    return [...this.events];
  }

  awardForDetections(detections: Detection[] = []): RewardResult {
    if (!detections.length) {
      return { addedPoints: 0, totalPoints: this.points, events: [] };
    }

    const now = Date.now();
    const newEvents: RewardEvent[] = [];
    let addedPoints = 0;

    detections.forEach((det) => {
      const key = `${det.class}:${det.class_group}`.toLowerCase();
      const lastAwarded = this.recentMap.get(key) ?? 0;
      if (now - lastAwarded < this.cooldownMs) {
        return;
      }

      const points = GROUP_POINTS[det.class_group] ?? 1;
      addedPoints += points;
      this.points += points;
      this.recentMap.set(key, now);

      const event: RewardEvent = {
        id: `${now}-${key}-${Math.random().toString(36).slice(2, 6)}`,
        timestamp: now,
        points,
        className: det.class,
        group: det.class_group,
        reason: `Phân loại ${det.class} (${det.class_group})`,
      };
      newEvents.push(event);
    });

    if (addedPoints > 0) {
      this.events = [...newEvents, ...this.events].slice(0, 20);
      this.persist();
    }

    return { addedPoints, totalPoints: this.points, events: newEvents };
  }

  private persist() {
    this.writeNumber(POINTS_KEY, this.points);
    this.writeJson(EVENTS_KEY, this.events);
    this.writeJson(RECENT_KEY, Array.from(this.recentMap.entries()));
  }

  private readNumber(key: string) {
    if (typeof window === 'undefined') return 0;
    const raw = window.localStorage.getItem(key);
    if (!raw) return 0;
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  private writeNumber(key: string, value: number) {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(key, value.toString());
  }

  private readJson<T>(key: string, fallback: T): T {
    if (typeof window === 'undefined') return fallback;
    try {
      const raw = window.localStorage.getItem(key);
      if (!raw) return fallback;
      return JSON.parse(raw);
    } catch {
      return fallback;
    }
  }

  private writeJson(key: string, value: unknown) {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(key, JSON.stringify(value));
  }
}

