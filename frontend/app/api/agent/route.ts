import { NextRequest, NextResponse } from "next/server";

const AGENT_API = process.env.AGENT_API_URL || "http://localhost:8080";

export async function POST(req: NextRequest) {
  const body = await req.json();

  try {
    const res = await fetch(`${AGENT_API}/agent/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
