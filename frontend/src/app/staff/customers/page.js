"use client";
import { useMemo, useState } from "react";
import Card from "@/components/common/Card";
import CustomerSearchBar from "@/components/staff/CustomerSearchBar";
import CustomerRow from "@/components/staff/CustomerRow";
import Skeleton from "@/components/common/Skeleton";
import { useCustomers } from "@/hooks/useCustomer";

export default function CustomersPage() {
  const { customers, loading } = useCustomers();
  const [query, setQuery] = useState("");
  const [persona, setPersona] = useState("");

  const personas = useMemo(() => [...new Set(customers.map((c) => c.persona))], [customers]);
  const filtered = customers.filter((c) => {
    const matchQ = `${c.name} ${c.location}`.toLowerCase().includes(query.toLowerCase());
    const matchP = !persona || c.persona === persona;
    return matchQ && matchP;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: "var(--text-3xl)" }}>Customers</h1>
        <p className="text-secondary" style={{ fontSize: "var(--text-sm)" }}>
          {customers.length} customers · click any to view agent reasoning.
        </p>
      </div>

      <CustomerSearchBar query={query} setQuery={setQuery} personas={personas}
        persona={persona} setPersona={setPersona} />

      <Card style={{ padding: 0, overflow: "hidden" }}>
        {loading && <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          {[...Array(6)].map((_, i) => <Skeleton key={i} height={42} />)}
        </div>}
        {!loading && filtered.map((c) => <CustomerRow key={c.id} customer={c} />)}
        {!loading && filtered.length === 0 && (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text-tertiary)" }}>No customers match.</div>
        )}
      </Card>
    </div>
  );
}
