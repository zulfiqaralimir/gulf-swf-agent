import ReactMarkdown from "react-markdown";

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

      <div className="text-xs text-slate-500 mb-4">
        {brief.filing_count} filing{brief.filing_count !== 1 ? "s" : ""} analyzed
      </div>

      <div className="max-h-[520px] overflow-y-auto pr-1 brief-content">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-base font-bold text-gold-400 mt-4 mb-2">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-sm font-bold text-gold-400 mt-4 mb-2">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-sm font-semibold text-slate-200 mt-3 mb-1">{children}</h3>
            ),
            p: ({ children }) => (
              <p className="text-sm text-slate-300 mb-2 leading-relaxed">{children}</p>
            ),
            strong: ({ children }) => (
              <strong className="text-slate-100 font-semibold">{children}</strong>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside space-y-1 mb-3 text-sm text-slate-300">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside space-y-1 mb-3 text-sm text-slate-300">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="text-slate-300 leading-relaxed">{children}</li>
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto mb-4">
                <table className="w-full text-xs border-collapse">{children}</table>
              </div>
            ),
            thead: ({ children }) => (
              <thead className="bg-navy-700">{children}</thead>
            ),
            th: ({ children }) => (
              <th className="px-3 py-2 text-left text-gold-400 font-semibold border border-navy-600">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="px-3 py-2 text-slate-300 border border-navy-600">{children}</td>
            ),
            tr: ({ children }) => (
              <tr className="hover:bg-navy-700/50 transition-colors">{children}</tr>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-2 border-gold-600 pl-3 italic text-slate-400 mb-2">
                {children}
              </blockquote>
            ),
            code: ({ children }) => (
              <code className="bg-navy-700 text-gold-400 px-1 rounded text-xs">{children}</code>
            ),
            hr: () => <hr className="border-navy-600 my-3" />,
          }}
        >
          {brief.brief_text || "No content."}
        </ReactMarkdown>
      </div>
    </div>
  );
}
