import { useCallback, useRef, useState } from 'react';
import { Detection, GroupSummaryItem } from '../types';

export interface DetectionHistoryEntry {
  id: string;
  timestamp: number;
  detections: Detection[];
  groupSummary?: Record<string, GroupSummaryItem>;
  pointsAwarded: number;
  signature: string;
}

const STORAGE_KEY = 'smartsort:history';

function readHistory(): DetectionHistoryEntry[] {
  if (typeof window === 'undefined') {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) ?? [];
  } catch {
    return [];
  }
}

function persistHistory(history: DetectionHistoryEntry[]) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

export function useDetectionHistory(limit = 30) {
  const [history, setHistory] = useState<DetectionHistoryEntry[]>(() => readHistory());
  const lastSignatureRef = useRef<string | null>(history[0]?.signature ?? null);

  const addEntry = useCallback(
    (entry: DetectionHistoryEntry) => {
      if (entry.signature === lastSignatureRef.current) {
        return;
      }
      lastSignatureRef.current = entry.signature;
      setHistory(prev => {
        const next = [entry, ...prev].slice(0, limit);
        persistHistory(next);
        return next;
      });
    },
    [limit]
  );

  const clearHistory = useCallback(() => {
    lastSignatureRef.current = null;
    setHistory([]);
    persistHistory([]);
  }, []);

  const exportJson = useCallback(() => {
    if (typeof window === 'undefined') return;
    const blob = new Blob([JSON.stringify(history, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `smartsort-history-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [history]);

  const exportCsv = useCallback(() => {
    if (typeof window === 'undefined') return;
    const header = 'timestamp,classes,groups,points\n';
    const rows = history
      .map(entry => {
        const classes = entry.detections.map(d => d.class).join('|');
        const groups = Object.entries(entry.groupSummary ?? {})
          .map(([key, value]) => `${key}:${value.count}`)
          .join('|');
        return `${new Date(entry.timestamp).toISOString()},${classes},${groups},${entry.pointsAwarded}`;
      })
      .join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `smartsort-history-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }, [history]);

  return {
    history,
    addEntry,
    clearHistory,
    exportJson,
    exportCsv,
  };
}

