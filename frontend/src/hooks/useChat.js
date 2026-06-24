"use client";
import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";

// Cache chat history per customer so returning to the Chat tab is instant.
const chatCache = new Map();

export function useChat(customerId) {
  const [messages, setMessages] = useState(() => chatCache.get(customerId) || []);
  const [typing, setTyping] = useState(false);
  const [language, setLanguage] = useState("en");
  const [loadingHistory, setLoadingHistory] = useState(() => !chatCache.has(customerId));

  useEffect(() => {
    if (!customerId) return;
    if (chatCache.has(customerId)) {
      setMessages(chatCache.get(customerId));
      setLoadingHistory(false);
      return;
    }
    const controller = new AbortController();
    setLoadingHistory(true);
    api.chatHistory(customerId, { signal: controller.signal })
      .then((rows) => { const r = rows || []; chatCache.set(customerId, r); setMessages(r); })
      .catch((e) => { if (e.name !== "AbortError") setMessages([]); })
      .finally(() => { if (!controller.signal.aborted) setLoadingHistory(false); });
    return () => controller.abort();
  }, [customerId]);

  // Keep the cache in sync as the conversation grows.
  useEffect(() => {
    if (customerId) chatCache.set(customerId, messages);
  }, [customerId, messages]);

  const send = useCallback(async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setTyping(true);
    try {
      const res = await api.chat({ customer_id: customerId, message: text, language });
      setMessages((m) => [...m, { role: "assistant", content: res.reply,
        sources: res.sources, quick_replies: res.quick_replies }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: `Sorry, I hit an error: ${e.message}` }]);
    } finally {
      setTyping(false);
    }
  }, [customerId, language]);

  return { messages, typing, send, language, setLanguage, loadingHistory };
}
