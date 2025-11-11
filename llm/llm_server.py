# llm_server.py
"""
Local LLM Server (Node 1) — Movie Ticket Booking System
-------------------------------------------------------
Runs a small, domain-specific LLM locally using Hugging Face Transformers.
This server answers FAQs and user queries related to movie bookings.

To run:
    pip install fastapi uvicorn transformers torch
    uvicorn llm_server:app --host 0.0.0.0 --port 8500 --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(
    title="Movie Booking Local LLM Server",
    description="Local transformer-based FAQ assistant for movie bookings.",
    version="2.0.0"
)

# -----------------------------
# Initialize local transformer model
# -----------------------------
# This is a lightweight, CPU-friendly model fine-tuned for Q&A
print("Loading local LLM model... (this may take ~30 seconds the first time)")
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# -----------------------------
# Domain-specific FAQ context
# -----------------------------
FAQ_CONTEXT = """
Our movie ticket booking system allows you to search, book, and cancel movie tickets in real time.
You can book tickets online for any available movie and showtime.
Bookings are confirmed only after successful payment.
Cancellations are allowed up to one hour before the showtime, and refunds are processed within 3–5 business days.
The system prevents overbooking using distributed consensus (Raft protocol) to ensure consistency across nodes.
Seat availability can be checked on the application or by using the /availability API.
If payment fails, no seat is reserved and you can retry the payment.
If the leader node fails, a new leader is automatically elected to maintain the booking state.
Support is available through support@movietix.ai.
"""

# -----------------------------
# Pydantic models
# -----------------------------
class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    confidence: float

# -----------------------------
# Routes
# -----------------------------
@app.get("/", tags=["health"])
def health():
    return {"status": "running", "model": "deepset/roberta-base-squad2"}

@app.post("/ask", response_model=Answer, tags=["faq"])
def ask_faq(q: Question):
    """
    Use a local transformer model to answer questions about the movie booking system.
    """
    try:
        result = qa_pipeline(question=q.question, context=FAQ_CONTEXT)
        answer = result.get("answer", "Sorry, I don't have an answer for that.")
        score = float(result.get("score", 0.0))
        return Answer(answer=answer, confidence=score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
