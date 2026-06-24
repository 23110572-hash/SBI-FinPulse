"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

/** Manage a customer's DPDP engagement consent. */
export function useConsent(customerId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const controllerRef = useRef(null);

  // `silent` skips the loading flag so an optimistic UI update isn't undone by
  // a flash of skeleton/disabled state while we reconcile with the server.
  const refresh = useCallback((silent = false) => {
    if (!customerId) return;
    if (controllerRef.current) controllerRef.current.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    if (!silent) setLoading(true);
    api.getConsent(customerId, { signal: controller.signal })
      .then(setData)
      .catch((e) => { if (e.name !== "AbortError") setData(null); })
      .finally(() => { if (!silent && !controller.signal.aborted) setLoading(false); });
  }, [customerId]);

  useEffect(() => {
    refresh();
    return () => { if (controllerRef.current) controllerRef.current.abort(); };
  }, [refresh]);

  const grant = useCallback(async (channels) => {
    if (!customerId) return;
    setBusy(true);
    const prev = data;
    // Optimistic: flip to Active immediately so the UI responds instantly.
    setData({
      customer_id: customerId,
      engagement_active: true,
      consents: [
        { id: "pending", customer_id: customerId, purpose: "proactive_engagement",
          status: "granted", channels: channels || ["email"],
          granted_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 365 * 864e5).toISOString() },
        ...((prev?.consents) || []),
      ],
    });
    try {
      await api.grantConsent(customerId, {
        purpose: "proactive_engagement",
        channels: channels || ["email"],
      });
      refresh(true);   // reconcile silently with the real server state
    } catch (e) {
      setData(prev);   // revert on failure
    } finally { setBusy(false); }
  }, [customerId, data, refresh]);

  const revoke = useCallback(async () => {
    if (!customerId) return;
    setBusy(true);
    const prev = data;
    // Optimistic: flip to Off immediately.
    setData({
      customer_id: customerId,
      engagement_active: false,
      consents: (prev?.consents || []).map((c) =>
        c.status === "granted" ? { ...c, status: "revoked", revoked_at: new Date().toISOString() } : c),
    });
    try {
      await api.revokeConsent(customerId, { purpose: "proactive_engagement" });
      refresh(true);
    } catch (e) {
      setData(prev);
    } finally { setBusy(false); }
  }, [customerId, data, refresh]);

  return {
    consents: data?.consents || [],
    active: !!data?.engagement_active,
    loading,
    busy,
    grant,
    revoke,
    refresh,
  };
}
