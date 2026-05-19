export default function IntelligenceBrief({ brief }: { brief: any }) {
  const date = brief.generated_at
    ? new Date(brief.generated_at).toLocaleString()
    : "—";

  return (
    <div className="card border-l-2 border-gold-500">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {(brief.funds_covered || []).map((f: string) => (
            <span
              key={f}
              className="badge bg-navy-700 text-gold-400 border border-gold-600"
            >
              {f}
            </span>
          ))}
        </div>
        <div className="text-xs text-slate-500 shrink-0">{date}</div>
      </div>

      <div className="text-xs text-slate-500 mb-2">
        {brief.filing_count} filing{brief.filing_count !== 1 ? "s" : ""} analyzed
      </div>

      <div className="prose prose-invert prose-sm max-w-none text-slate-300 whitespace-pre-wrap text-sm leading-relaxed max-h-80 overflow-y-auto">
        {brief.brief_text || "No content."}
      </div>
    </div>
  );
}
