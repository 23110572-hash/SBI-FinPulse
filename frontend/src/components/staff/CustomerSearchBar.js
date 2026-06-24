"use client";
import { Search } from "lucide-react";

export default function CustomerSearchBar({ query, setQuery, personas = [], persona, setPersona }) {
  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      <div style={{ position: "relative", flex: 1, minWidth: 220 }}>
        <Search size={18} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)",
          color: "var(--text-tertiary)" }} />
        <input value={query} onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name or city..."
          style={{ width: "100%", padding: "11px 14px 11px 42px", borderRadius: "var(--radius-md)",
            border: "1px solid var(--neutral-300)", fontSize: "var(--text-sm)", outline: "none" }} />
      </div>
      <select value={persona} onChange={(e) => setPersona(e.target.value)}
        style={{ padding: "11px 14px", borderRadius: "var(--radius-md)", border: "1px solid var(--neutral-300)",
          fontSize: "var(--text-sm)", background: "#fff", color: "var(--text-primary)" }}>
        <option value="">All personas</option>
        {personas.map((p) => <option key={p} value={p}>{p}</option>)}
      </select>
    </div>
  );
}
