const FORM_COLORS: Record<string, string> = {
  "SC 13D":   "bg-red-900/40 text-red-300 border-red-700",
  "SC 13D/A": "bg-orange-900/40 text-orange-300 border-orange-700",
  "SC 13G":   "bg-blue-900/40 text-blue-300 border-blue-700",
  "SC 13G/A": "bg-indigo-900/40 text-indigo-300 border-indigo-700",
};

const FUND_COLORS: Record<string, string> = {
  ADIA:     "text-emerald-400",
  PIF:      "text-green-400",
  QIA:      "text-teal-400",
  MUBADALA: "text-cyan-400",
};

export default function FilingCard({ filing }: { filing: any }) {
  const formClass = FORM_COLORS[filing.form_type] || "bg-slate-800 text-slate-300 border-slate-600";
  const fundClass = FUND_COLORS[filing.fund] || "text-gold-400";

  return (
    <div className="card flex items-start justify-between gap-4 hover:border-navy-500 transition-colors">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-sm font-semibold ${fundClass}`}>{filing.fund}</span>
          <span className={`badge border ${formClass}`}>{filing.form_type}</span>
          {filing.needs_gemini_parse && (
            <span className="badge bg-yellow-900/40 text-yellow-300 border border-yellow-700">
              needs parse
            </span>
          )}
        </div>
        <p className="text-slate-200 font-medium mt-1 truncate">
          {filing.issuer_name || "Issuer pending extraction"}
        </p>
        {filing.cusip && (
          <p className="text-xs text-slate-500 mt-0.5">CUSIP: {filing.cusip}</p>
        )}
      </div>

      <div className="text-right shrink-0 space-y-1">
        <div className="text-xs text-slate-500">{filing.filing_date}</div>
        {filing.ownership_pct != null && (
          <div className="text-sm font-semibold text-gold-400">
            {filing.ownership_pct}%
          </div>
        )}
        {filing.shares_held != null && (
          <div className="text-xs text-slate-400">
            {filing.shares_held.toLocaleString()} shares
          </div>
        )}
        {filing.url && (
          <a
            href={filing.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-slate-600 hover:text-gold-400 transition-colors"
          >
            SEC filing →
          </a>
        )}
      </div>
    </div>
  );
}
