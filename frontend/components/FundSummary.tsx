const COUNTRY_FLAG: Record<string, string> = {
  UAE:          "🇦🇪",
  "Saudi Arabia": "🇸🇦",
  Qatar:        "🇶🇦",
};

export default function FundSummary({ fund }: { fund: any }) {
  const flag = COUNTRY_FLAG[fund.country] || "🏦";

  return (
    <a href={`/funds/${fund.name}`} className="card hover:border-gold-500 transition-colors block">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{flag}</span>
        <span className="font-bold text-gold-400 text-lg">{fund.name}</span>
      </div>
      <p className="text-xs text-slate-400 leading-snug">{fund.full_name}</p>
      {fund.aum_usd_trillion && (
        <p className="text-xs text-slate-500 mt-2">
          AUM: <span className="text-slate-300">${fund.aum_usd_trillion}T</span>
        </p>
      )}
      {fund.focus_sectors && (
        <div className="flex flex-wrap gap-1 mt-2">
          {fund.focus_sectors.slice(0, 2).map((s: string) => (
            <span key={s} className="badge bg-navy-700 text-slate-400 text-[10px]">{s}</span>
          ))}
        </div>
      )}
    </a>
  );
}
