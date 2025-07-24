import os
import time
import threading
from dotenv import load_dotenv
from aai import VoiceTranscriber
from gemini import AIHandler  # Your earlier class with context and streaming

load_dotenv()

QUESTIONS = [
    "Can you briefly describe your backend tech stack and why you chose it?",
    "How would you implement authentication and authorization in a FastAPI app?",
    "What are some challenges you've faced while scaling a backend system?",
    "How do you design APIs to ensure they are versioned, documented, and user-friendly?",
    "Explain how you might use Redis in a backend service.",
]


class InterviewCLI:
    def __init__(self):
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            raise ValueError("Missing ASSEMBLYAI_API_KEY in environment")

        self.questions = QUESTIONS
        self.current_question_index = 0
        self.last_answer = ""
        self.answer_complete = False
        self.transcriber_thread = None

        self.ai = AIHandler(self.questions)
        self.transcriber = VoiceTranscriber(
            api_key=api_key,
            on_transcript=self.on_transcript
        )

    def on_transcript(self, text: str, end_of_turn: bool):
        print(f"🗣️ Transcript chunk: {text.strip()} (Aai end_of_turn={end_of_turn})")
        self.last_answer += " " + text
        if end_of_turn:
            print("✅ Detected end of turn from AssemblyAI")
            self.answer_complete = True
            print(f"🎯 answer_complete = {self.answer_complete}")
            self.transcriber.stop()

    def ask_next_question(self):
        question = self.questions[self.current_question_index]
        print(f"\n❓ Question {self.current_question_index + 1}: {question}")
        return question

    def run_transcriber(self):
        self.transcriber.run()

    def run(self):
        print("🎙️ Welcome to the Voice Interview CLI\n")
        while self.current_question_index < len(self.questions):
            question = self.ask_next_question()
            print("🎤 Speak your answer...")

            self.last_answer = ""
            self.answer_complete = False

            # Start transcriber in a separate thread
            self.transcriber_thread = threading.Thread(target=self.run_transcriber)
            self.transcriber_thread.start()

            # Wait until transcription marks the answer as complete
            while not self.answer_complete:
                time.sleep(0.1)

            self.transcriber_thread.join()

            print("\n📩 Answer received:")
            print(self.last_answer.strip())

            # Evaluate with Gemini AI (streaming)
            print("\n🤖 Sending answer to Gemini for feedback...")
            print("💬 Gemini:", end=" ", flush=True)

            for chunk in self.ai.stream_response(question, self.last_answer.strip()):
                print(chunk, end="", flush=True)

            print("\n✅ Gemini finished responding.")

            self.current_question_index += 1
            input("\n⏭️ Press Enter to continue to the next question...")

        print("\n✅ Interview complete. Thank you!")


if __name__ == "__main__":
    cli = InterviewCLI()
    cli.run()
