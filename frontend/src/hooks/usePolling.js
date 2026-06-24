"use client";
import { useEffect, useRef } from "react";

/**
 * Calls `fn` on an interval, but:
 *  - runs once immediately,
 *  - pauses while the browser tab is hidden (no background traffic),
 *  - never lets two runs overlap (awaits the previous one),
 *  - resumes + refreshes the moment the tab becomes visible again.
 *
 * `fn` may return a promise. Keep `fn` stable (useCallback) or rely on the
 * ref capture below.
 */
export function usePolling(fn, intervalMs = 15000, enabled = true) {
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    if (!enabled) return;
    let timer = null;
    let inFlight = false;
    let stopped = false;

    const tick = async () => {
      if (stopped || inFlight) return;
      if (typeof document !== "undefined" && document.hidden) return;
      inFlight = true;
      try { await fnRef.current(); } catch (_) {} finally { inFlight = false; }
    };

    tick(); // immediate
    timer = setInterval(tick, intervalMs);

    const onVisible = () => { if (!document.hidden) tick(); };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      stopped = true;
      clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [intervalMs, enabled]);
}
