"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "@/lib/api";

// Cache analysis per customer so switching tabs (home ↔ insights) is instant.
const analysisCache = new Map();

// Fetch the latest stored analysis (wellness, insights, nudges) for a customer.
export function useAnalysis(customerId) {
  const [analysis, setAnalysis] = useState(() => analysisCache.get(customerId) || null);
  const [loading, setLoading] = useState(() => !analysisCache.has(customerId));
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);

  const load = useCallback(() => {
    if (!customerId) return;
    // Abort any in-flight load for the previous (or same) customer.
    if (controllerRef.current) controllerRef.current.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    if (!analysisCache.has(customerId)) setLoading(true);
    api.getAnalysis(customerId, { signal: controller.signal })
      .then((d) => { analysisCache.set(customerId, d); setAnalysis(d); })
      .catch((e) => { if (e.name !== "AbortError") setError(e.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
  }, [customerId]);

  useEffect(() => {
    const cached = analysisCache.get(customerId);
    if (cached) {
      setAnalysis(cached);
      setLoading(false);
    } else {
      setAnalysis(null);   // clear previous account's analysis on switch
    }
    load();
    return () => { if (controllerRef.current) controllerRef.current.abort(); };
  }, [customerId, load]);

  return { analysis, loading, error, reload: load };
}

// Stream a live crew run via SSE, collecting per-step logs.
export function useAnalysisStream(customerId) {
  const [steps, setSteps] = useState({});       // step -> {status, log}
  const [stepPlan, setStepPlan] = useState([]);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const esRef = useRef(null);

  const start = useCallback(() => {
    if (!customerId) return;
    // Close any prior stream before starting a new one — switching customers
    // mid-run was leaving orphan EventSources alive, hammering renders.
    if (esRef.current) {
      try { esRef.current.close(); } catch (_) {}
      esRef.current = null;
    }
    setSteps({});
    setResult(null);
    setError(null);
    setRunning(true);

    const es = new EventSource(api.streamUrl(customerId));
    esRef.current = es;

    es.addEventListener("steps", (e) => {
      try { setStepPlan(JSON.parse(e.data)); } catch (_) {}
    });

    es.onmessage = (e) => {
      let data;
      try { data = JSON.parse(e.data); } catch (_) { return; }
      if (data.type === "step") {
        setSteps((prev) => ({ ...prev, [data.step]: { status: data.status, log: data.log } }));
      } else if (data.type === "done") {
        setResult(data.result);
      } else if (data.type === "error") {
        setError(data.message);
      }
    };

    es.addEventListener("end", () => { setRunning(false); es.close(); });
    es.onerror = () => { setRunning(false); es.close(); };
  }, [customerId]);

  // When the active customer changes, fully reset the stream: close any live
  // EventSource AND clear running/result/steps/error. Previously only the
  // socket was closed, so the PREVIOUS customer's `running`/`result` lingered
  // and blocked the new customer's auto-start (the switch appeared to do
  // nothing, or showed the old account's reasoning). Resetting here lets the
  // home page's auto-start effect fire cleanly for the newly selected account.
  useEffect(() => {
    if (esRef.current) {
      try { esRef.current.close(); } catch (_) {}
      esRef.current = null;
    }
    setSteps({});
    setStepPlan([]);
    setResult(null);
    setError(null);
    setRunning(false);

    return () => {
      if (esRef.current) {
        try { esRef.current.close(); } catch (_) {}
        esRef.current = null;
      }
    };
  }, [customerId]);

  return { steps, stepPlan, result, running, error, start };
}
