"use client";
import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";

const KEY = "finpulse_customer_id";

// Module-level caches so switching tabs doesn't refetch (instant navigation).
const customerCache = new Map();
let customersListCache = null;

export function getStoredCustomerId() {
  if (typeof window === "undefined") return "CUST_001";
  return localStorage.getItem(KEY) || "CUST_001";
}

export function setStoredCustomerId(id) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, id);
}

// Shared, reactive store for the active customer id so EVERY mounted
// useCustomerId() consumer updates together the moment an account is switched
// (previously each component held its own state and could drift out of sync).
let _currentId = null;
const _idListeners = new Set();

export function useCustomerId() {
  const [id, setId] = useState("CUST_001");

  useEffect(() => {
    if (_currentId === null) _currentId = getStoredCustomerId();
    setId(_currentId);
    _idListeners.add(setId);
    return () => { _idListeners.delete(setId); };
  }, []);

  const update = useCallback((newId) => {
    if (!newId || newId === _currentId) return;
    _currentId = newId;
    setStoredCustomerId(newId);
    _idListeners.forEach((fn) => fn(newId));   // notify all mounted consumers
  }, []);

  return [id, update];
}

export function useCustomer(customerId) {
  const [customer, setCustomer] = useState(() => customerCache.get(customerId) || null);
  const [loading, setLoading] = useState(() => !customerCache.has(customerId));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!customerId) return;
    const controller = new AbortController();
    let active = true;

    const cached = customerCache.get(customerId);
    if (cached) {
      setCustomer(cached);
      setLoading(false);
    } else {
      setCustomer(null);   // clear stale data so the switch is visible immediately
      setLoading(true);
    }

    // Revalidate in the background (kept fresh without blocking the UI).
    api.getCustomer(customerId, { signal: controller.signal })
      .then((d) => { customerCache.set(customerId, d); if (active) setCustomer(d); })
      .catch((e) => { if (active && e.name !== "AbortError") setError(e.message); })
      .finally(() => active && setLoading(false));

    return () => { active = false; controller.abort(); };
  }, [customerId]);

  return { customer, loading, error };
}

export function useCustomers() {
  const [customers, setCustomers] = useState(() => customersListCache || []);
  const [loading, setLoading] = useState(() => !customersListCache);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    if (customersListCache) setLoading(false);

    api.listCustomers({ signal: controller.signal })
      .then((d) => { customersListCache = d; if (active) setCustomers(d); })
      .catch((e) => { if (active && e.name !== "AbortError") setError(e.message); })
      .finally(() => active && setLoading(false));

    return () => { active = false; controller.abort(); };
  }, []);

  return { customers, loading, error };
}
