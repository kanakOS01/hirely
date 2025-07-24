import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class AIHandler:
    def __init__(self, questions: list[str]):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Start chat with initial context
        self.chat = self.model.start_chat(history=[])
        self.questions = questions

        # Prime the model with full interview context
        self._initialize_chat_context()

    def _initialize_chat_context(self):
        joined_questions = "\n".join(f"{i+1}. {q}" for i, q in enumerate(self.questions))
        intro = (
            "You are a technical interviewer evaluating a backend developer. "
            "Below is the full list of questions you'll be asking the candidate:\n\n"
            f"{joined_questions}\n\n"
            "For each response, provide concise feedback. "
            "If the answer is vague or incomplete, you can ask clarifying questions. "
            "If there's no answer, politely move on.\n"
            "Be conversational and constructive."
        )
        self.chat.send_message(intro)

    def handle_question_streaming(self, question: str, answer: str):
        """
        Yields streamed response chunks for a given question and answer.
        """
        if not answer.strip():
            self.chat.send_message(
                f"The candidate did not answer the question: '{question}'"
            )
            yield "No answer received. Moving to the next question.\n"
            return

        prompt = (
            f"Question:\n{question}\n\n"
            f"Candidate's Answer:\n{answer}\n\n"
            "Please provide feedback. If clarification is needed, ask a follow-up."
        )

        response_stream = self.chat.send_message(prompt, stream=True)
        for chunk in response_stream:
            yield chunk.text
