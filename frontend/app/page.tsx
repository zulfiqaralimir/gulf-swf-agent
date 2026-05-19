"use client";

import { useState, useEffect } from "react";
import FilingCard from "@/components/FilingCard";
import IntelligenceBrief from "@/components/IntelligenceBrief";
import AgentStatus from "@/components/AgentStatus";
import FundSummary from "@/components/FundSummary";

const AGENT_API = process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8080";

export default function DashboardPage() {
  const [filings, setFilings] = useState<any[]>([]);
  const [briefs, setBriefs] = useState<any[]>([]);
  const [funds, setFunds] = useState<any[]>([]);
  const [agentRunning, setAgentRunning] = useState(false);
  const [agentResponse, setAgentResponse] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [loading, setLoading] = useState(true);

  async function fetchData() {
    try {
      const [filingsRes, briefsRes, fundsRes] = await Promise.all([
        fetch(`${AGENT_API}/api/filings?limit=10`),
        fetch(`${AGENT_API}/api/intelligence?limit=3`),
        fetch(`${AGENT_API}/api/funds`),
      ]);
      if (filingsRes.ok) setFilings(await filingsRes.json());
      if (briefsRes.ok) setBriefs(await briefsRes.json());
      if (fundsRes.ok) setFunds(await fundsRes.json());
    } catch {
      // Backend not yet connected — show empty state
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchData(); }, []);

  async function runAgent() {
    setAgentRunning(true);
    setAgentResponse("");
    try {
      const res = await fetch(`${AGENT_API}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: "Monitor SEC EDGAR for new Gulf SWF 13D/13G filings from the past 30 days. Parse, store in MongoDB, and generate an intelligence brief.",
        }),
      });
      const data = await res.json();
      setAgentResponse(data.response);
      await fetchData();
    } catch (e: any) {
      setAgentResponse(`Error: ${e.message}`);
    } finally {
      setAgentRunning(false);
    }
  }

  async function sendChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setAgentRunning(true);
    setAgentResponse("");
    try {
      const res = await fetch(`${AGENT_API}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatInput }),
      });
      const data = await res.json();
      setAgentResponse(data.response);
      setChatInput("");
    } catch (e: any) {
      setAgentResponse(`Error: ${e.message}`);
    } finally {
      setAgentRunning(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Filings", value: filings.length || "—" },
          { label: "Active SWFs", value: funds.length || 4 },
          { label: "Intelligence Briefs", value: briefs.length || "—" },
          { label: "Latest Filing", value: filings[0]?.filing_date || "—" },
        ].map((stat) => (
          <div key={stat.label} className="card text-center">
            <div className="text-2xl font-bold text-gold-400">{stat.value}</div>
            <div className="text-xs text-slate-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Fund summaries */}
      <section>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Monitored Funds
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(funds.length ? funds : PLACEHOLDER_FUNDS).map((f) => (
            <FundSummary key={f.name} fund={f} />
          ))}
        </div>
      </section>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Agent control */}
        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Agent Control
          </h2>
          <div className="card space-y-4">
            <AgentStatus running={agentRunning} />
            <button onClick={runAgent} disabled={agentRunning} className="btn-gold w-full">
              {agentRunning ? "Running..." : "Run Agent — Fetch Latest Filings"}
            </button>
            <form onSubmit={sendChat} className="flex gap-2">
              <input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask the agent anything..."
                className="flex-1 bg-navy-700 border border-navy-600 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-gold-500"
              />
              <button type="submit" disabled={agentRunning} className="btn-outline text-sm">
                Ask
              </button>
            </form>
            {agentResponse && (
              <div className="bg-navy-900 rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap max-h-64 overflow-y-auto">
                {agentResponse}
              </div>
            )}
          </div>
        </section>

        {/* Latest intelligence brief */}
        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Latest Intelligence Brief
          </h2>
          {briefs.length > 0 ? (
            <IntelligenceBrief brief={briefs[0]} />
          ) : (
            <div className="card text-slate-500 text-sm">
              No briefs yet. Run the agent to generate the first brief.
            </div>
          )}
        </section>
      </div>

      {/* Recent filings */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
            Recent Filings
          </h2>
          <a href="/filings" className="text-xs text-gold-400 hover:text-gold-300">
            View all →
          </a>
        </div>
        {loading ? (
          <div className="text-slate-500 text-sm">Loading...</div>
        ) : filings.length > 0 ? (
          <div className="space-y-3">
            {filings.map((f, i) => (
              <FilingCard key={i} filing={f} />
            ))}
          </div>
        ) : (
          <div className="card text-slate-500 text-sm">
            No filings stored yet. Run the agent to fetch filings from SEC EDGAR.
          </div>
        )}
      </section>
    </div>
  );
}

const PLACEHOLDER_FUNDS = [
  { name: "ADIA", full_name: "Abu Dhabi Investment Authority", country: "UAE", aum_usd_trillion: 1.1 },
  { name: "PIF", full_name: "Public Investment Fund", country: "Saudi Arabia", aum_usd_trillion: 0.93 },
  { name: "QIA", full_name: "Qatar Investment Authority", country: "Qatar", aum_usd_trillion: 0.45 },
  { name: "MUBADALA", full_name: "Mubadala Investment Company", country: "UAE", aum_usd_trillion: 0.28 },
];
