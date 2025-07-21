import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const apiKey = process.env.ASSEMBLYAI_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ error: "No API key set" }, { status: 500 });
  }
  // Get a temporary token from AssemblyAI
  const resp = await fetch("https://api.assemblyai.com/v2/realtime/token", {
    method: "POST",
    headers: {
      authorization: apiKey,
      "content-type": "application/json"
    },
    body: JSON.stringify({ expires_in: 60 * 60 }) // 1 hour
  });
  if (!resp.ok) {
    return NextResponse.json({ error: "Failed to get token" }, { status: 500 });
  }
  const data = await resp.json();
  return NextResponse.json({ token: data.token });
} 