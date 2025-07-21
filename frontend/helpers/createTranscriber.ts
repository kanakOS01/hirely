export function createTranscriber(token: string) {
  const wsUrl = `wss://api.assemblyai.com/v2/realtime/ws?token=${token}`;
  const ws = new WebSocket(wsUrl);
  return ws;
} 