import { NextRequest, NextResponse } from "next/server";

const AGENT_API = process.env.AGENT_API_URL || "http://localhost:8080";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const params = new URLSearchParams();
  if (searchParams.get("fund")) params.set("fund", searchParams.get("fund")!);
  if (searchParams.get("limit")) params.set("limit", searchParams.get("limit")!);

  try {
    const res = await fetch(`${AGENT_API}/api/filings?${params}`, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json([], { status: 200 });
  }
}
