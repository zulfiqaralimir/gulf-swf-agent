import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gulf SWF Intelligence Agent",
  description: "Real-time SEC 13D/13G filing intelligence for Gulf Sovereign Wealth Funds",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-navy-900 text-slate-200 antialiased">
        <header className="border-b border-navy-600 bg-navy-800/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gold-500 flex items-center justify-center font-bold text-navy-900 text-sm">
                SWF
              </div>
              <span className="font-semibold text-lg text-slate-100">
                Gulf SWF Intelligence
              </span>
            </div>
            <nav className="flex items-center gap-6 text-sm text-slate-400">
              <a href="/" className="hover:text-gold-400 transition-colors">Dashboard</a>
              <a href="/filings" className="hover:text-gold-400 transition-colors">Filings</a>
              <a href="/funds/ADIA" className="hover:text-gold-400 transition-colors">Funds</a>
            </nav>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
        <footer className="border-t border-navy-600 mt-16">
          <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-slate-600 text-center">
            Gulf SWF Intelligence Agent — Google Cloud ADK + MongoDB — Built for Google Cloud Rapid Agent Hackathon
          </div>
        </footer>
      </body>
    </html>
  );
}
