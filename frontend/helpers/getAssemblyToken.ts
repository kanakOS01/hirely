export async function getAssemblyToken(): Promise<string> {
  const res = await fetch("/api/assemblyToken");
  if (!res.ok) throw new Error("Failed to get AssemblyAI token");
  const data = await res.json();
  return data.token;
} 