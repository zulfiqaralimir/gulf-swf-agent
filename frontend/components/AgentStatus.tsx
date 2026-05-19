export default function AgentStatus({ running }: { running: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${
          running ? "bg-gold-400 animate-pulse" : "bg-emerald-500"
        }`}
      />
      <span className="text-sm text-slate-400">
        Agent: <span className={running ? "text-gold-400" : "text-emerald-400"}>
          {running ? "Running..." : "Ready"}
        </span>
      </span>
    </div>
  );
}
