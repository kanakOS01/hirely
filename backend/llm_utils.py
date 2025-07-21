import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

async def get_feedback(transcript: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = (
        "You are an interview coach. Give constructive, actionable feedback on the following interview answer. "
        "Be specific and concise.\n\nAnswer: " + transcript
    )
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, 'text') else str(response) 