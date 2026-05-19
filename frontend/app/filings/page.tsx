"use client";

import { useState, useEffect } from "react";
import FilingCard from "@/components/FilingCard";

const AGENT_API = process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8080";
const FUNDS = ["All", "ADIA", "PIF", "QIA", "MUBADALA"];
const FORMS = ["All", "SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"];

export default function FilingsPage() {
  const [filings, setFilings] = useState<any[]>([]);
  const [selectedFund, setSelectedFund] = useState("All");
  const [selectedForm, setSelectedForm] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const params = new URLSearchParams({ limit: "100" });
        if (selectedFund !== "All") params.set("fund", selectedFund);
        const res = await fetch(`${AGENT_API}/api/filings?${params}`);
        if (res.ok) setFilings(await res.json());
      } catch {}
      setLoading(false);
    }
    load();
  }, [selectedFund]);

  const filtered =
    selectedForm === "All"
      ? filings
      : filings.filter((f) => f.form_type === selectedForm);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">All Filings</h1>
        <span className="text-sm text-slate-500">{filtered.length} records</span>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="flex gap-2">
          {FUNDS.map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFund(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                selectedFund === f
                  ? "bg-gold-500 text-navy-900"
                  : "bg-navy-800 text-slate-400 hover:text-slate-200 border border-navy-600"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          {FORMS.map((f) => (
            <button
              key={f}
              onClick={() => setSelectedForm(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                selectedForm === f
                  ? "bg-navy-700 text-gold-400 border border-gold-500"
                  : "bg-navy-800 text-slate-400 hover:text-slate-200 border border-navy-600"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading...</div>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((f, i) => (
            <FilingCard key={i} filing={f} />
          ))}
        </div>
      ) : (
        <div className="card text-slate-500 text-sm">
          No filings match the current filters. Run the agent from the dashboard to fetch data.
        </div>
      )}
    </div>
  );
}
