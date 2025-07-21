"use client";
import React, { useState } from "react";
import { Button, Container, Typography, Box, Paper } from "@mui/material";
import { getAssemblyToken } from "../helpers/getAssemblyToken";
import { createTranscriber } from "../helpers/createTranscriber";

const questions = [
  "Tell me about yourself.",
  "Why are you interested in this role?",
  "Describe a challenge you faced at work.",
  "How do you handle feedback?",
  "Where do you see yourself in 5 years?"
];

export default function InterviewPage() {
  const [current, setCurrent] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [feedback, setFeedback] = useState("");
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [audioSource, setAudioSource] = useState<MediaStreamAudioSourceNode | null>(null);
  const [processor, setProcessor] = useState<ScriptProcessorNode | null>(null);

  // Placeholder for mic/AssemblyAI integration
  const handleStart = async () => {
    setRecording(true);
    setTranscript("");
    setFeedback("");
    // Get AssemblyAI token
    const token = await getAssemblyToken();
    const ws = createTranscriber(token);
    setWs(ws);
    // Set up mic
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    setMediaStream(stream);
    const audioCtx = new window.AudioContext();
    setAudioContext(audioCtx);
    const source = audioCtx.createMediaStreamSource(stream);
    setAudioSource(source);
    const processor = audioCtx.createScriptProcessor(4096, 1, 1);
    setProcessor(processor);
    source.connect(processor);
    processor.connect(audioCtx.destination);
    processor.onaudioprocess = (e) => {
      if (ws.readyState !== 1) return;
      const input = e.inputBuffer.getChannelData(0);
      // Convert to 16-bit PCM
      const buffer = new ArrayBuffer(input.length * 2);
      const view = new DataView(buffer);
      for (let i = 0; i < input.length; i++) {
        let s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      }
      ws.send(buffer);
    };
    ws.onmessage = (msg) => {
      const res = JSON.parse(msg.data);
      if (res.text) setTranscript(res.text);
    };
    ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };
    ws.onclose = () => {
      // Clean up
      processor.disconnect();
      source.disconnect();
      audioCtx.close();
      setWs(null);
      setMediaStream(null);
      setAudioContext(null);
      setAudioSource(null);
      setProcessor(null);
    };
  };
  const handleStop = () => {
    setRecording(false);
    if (processor) processor.disconnect();
    if (audioSource) audioSource.disconnect();
    if (audioContext) audioContext.close();
    if (mediaStream) mediaStream.getTracks().forEach((t) => t.stop());
    if (ws && ws.readyState === 1) ws.close();
  };
  const handleGetFeedback = async () => {
    setLoading(true);
    // TODO: Send transcript to backend
    const res = await fetch("http://localhost:8000/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript })
    });
    const data = await res.json();
    setFeedback(data.feedback);
    setLoading(false);
  };
  const handleNext = () => {
    setCurrent((prev) => prev + 1);
    setTranscript("");
    setFeedback("");
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Interview Question {current + 1} of {questions.length}
        </Typography>
        <Typography variant="h6" sx={{ mb: 3 }}>
          {questions[current]}
        </Typography>
        <Box sx={{ mb: 2 }}>
          <Button
            variant={recording ? "contained" : "outlined"}
            color={recording ? "error" : "primary"}
            onClick={recording ? handleStop : handleStart}
            disabled={!!feedback}
          >
            {recording ? "Stop Recording" : "Start Answer"}
          </Button>
        </Box>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">Transcript:</Typography>
          <Paper variant="outlined" sx={{ p: 2, minHeight: 60 }}>
            {transcript || <span style={{ color: '#aaa' }}>[Your answer will appear here]</span>}
          </Paper>
        </Box>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            onClick={handleGetFeedback}
            disabled={!transcript || !!feedback || loading}
          >
            {loading ? "Getting Feedback..." : "Get Feedback"}
          </Button>
        </Box>
        {feedback && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1">Feedback:</Typography>
            <Paper variant="outlined" sx={{ p: 2, minHeight: 60 }}>
              {feedback}
            </Paper>
          </Box>
        )}
        <Button
          variant="text"
          onClick={handleNext}
          disabled={!feedback || current === questions.length - 1}
        >
          Next Question
        </Button>
      </Paper>
    </Container>
  );
}
