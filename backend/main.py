from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llm_utils import get_feedback

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    transcript: str

class FeedbackResponse(BaseModel):
    feedback: str

@app.post("/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest):
    feedback = await get_feedback(req.transcript)
    return FeedbackResponse(feedback=feedback) 