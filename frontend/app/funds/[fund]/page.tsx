"use client";

import { useState, useEffect } from "react";
import FilingCard from "@/components/FilingCard";
import IntelligenceBrief from "@/components/IntelligenceBrief";

const AGENT_API = process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8080";

export default function FundPage({ params }: { params: { fund: string } }) {
  const fund = params.fund.toUpperCase();
  const [filings, setFilings] = useState<any[]>([]);
  const [briefs, setBriefs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [fr, br] = await Promise.all([
          fetch(`${AGENT_API}/api/filings?fund=${fund}&limit=20`),
          fetch(`${AGENT_API}/api/intelligence?limit=5`),
        ]);
        if (fr.ok) setFilings(await fr.json());
        if (br.ok) {
          const all = await br.json();
          setBriefs(all.filter((b: any) => b.funds_covered?.includes(fund)));
        }
      } catch {}
      setLoading(false);
    }
    load();
  }, [fund]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">{fund}</h1>
        <p className="text-slate-500 mt-1">SEC 13D/13G filing intelligence</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Filings Stored", value: filings.length },
          { label: "Latest Date", value: filings[0]?.filing_date || "—" },
          { label: "Unique Issuers", value: new Set(filings.map((f) => f.issuer_name)).size || "—" },
        ].map((s) => (
          <div key={s.label} className="card text-center">
            <div className="text-2xl font-bold text-gold-400">{s.value}</div>
            <div className="text-xs text-slate-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Filings
          </h2>
          {loading ? (
            <div className="text-slate-500 text-sm">Loading...</div>
          ) : filings.length > 0 ? (
            <div className="space-y-3">
              {filings.map((f, i) => <FilingCard key={i} filing={f} />)}
            </div>
          ) : (
            <div className="card text-slate-500 text-sm">No filings stored for {fund}.</div>
          )}
        </section>

        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Intelligence Briefs
          </h2>
          {briefs.length > 0 ? (
            <div className="space-y-4">
              {briefs.map((b, i) => <IntelligenceBrief key={i} brief={b} />)}
            </div>
          ) : (
            <div className="card text-slate-500 text-sm">No briefs covering {fund} yet.</div>
          )}
        </section>
      </div>
    </div>
  );
}
