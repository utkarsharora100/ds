# llm_server.py
"""
Local LLM Server — Movie Ticket Booking System
-------------------------------------------------------
Runs Qwen2.5-0.5B model locally using Hugging Face Transformers.
This server provides chat-based assistance and FAQ support for movie bookings.

Model: Qwen/Qwen2.5-0.5B (500M parameters, lightweight and fast)

To run:
    pip install fastapi uvicorn transformers torch accelerate
    python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500
"""

import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(
    title="Movie Booking LLM Server (Qwen2.5)",
    description="Conversational AI assistant for movie booking system powered by Qwen2.5-0.5B",
    version="3.0.0"
)

# Add CORS middleware for Docker environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Configuration
# -----------------------------
MODEL_NAME = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-0.5B")
MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# System prompt for movie booking assistant
SYSTEM_PROMPT = """You are a helpful AI assistant for a distributed movie ticket booking system. 

Key Information:
- Users can search, book, and cancel movie tickets in real-time
- Bookings require successful payment to be confirmed
- Cancellations are allowed up to 1 hour before showtime
- Refunds are processed within 3-5 business days
- The system uses Raft consensus protocol for data consistency
- Seat availability can be checked via the application or API
- Failed payments don't reserve seats - users can retry
- If a node fails, a new leader is automatically elected
- Support: support@movietix.ai

Please provide helpful, concise answers about the booking system."""

# -----------------------------
# Global model variables
# -----------------------------
tokenizer = None
model = None
text_gen_pipeline = None

# -----------------------------
# Initialize model on startup
# -----------------------------
@app.on_event("startup")
async def load_model():
    global tokenizer, model, text_gen_pipeline
    
    print(f"🤖 Loading LLM model: {MODEL_NAME}")
    print("⏳ This may take 30-60 seconds on first run...")
    
    try:
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Also create a pipeline for simpler text generation
        text_gen_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True
        )
        
        device = "CUDA" if torch.cuda.is_available() else "CPU"
        print(f"✅ Model loaded successfully on {device}")
        print(f"📊 Model parameters: ~500M")
        print(f"🎯 Max tokens: {MAX_NEW_TOKENS}, Temperature: {TEMPERATURE}")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise

# -----------------------------
# Pydantic models
# -----------------------------
class Message(BaseModel):
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="Conversation history")
    max_tokens: Optional[int] = Field(None, description="Override max tokens")
    temperature: Optional[float] = Field(None, description="Override temperature")

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None

class QuestionRequest(BaseModel):
    question: str = Field(..., description="User question")

class QuestionResponse(BaseModel):
    answer: str
    question: str
    model: str

# -----------------------------
# Routes
# -----------------------------
@app.get("/", tags=["health"])
def root():
    return {
        "status": "running",
        "model": MODEL_NAME,
        "service": "llm-server",
        "version": "3.0.0",
        "endpoints": {
            "chat": "/chat",
            "ask": "/ask",
            "health": "/health"
        }
    }

@app.get("/health", tags=["health"])
def health_check():
    model_loaded = model is not None and tokenizer is not None
    return {
        "status": "healthy" if model_loaded else "loading",
        "service": "llm-server",
        "model": MODEL_NAME,
        "model_loaded": model_loaded,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint using Qwen2.5 with conversation history.
    Supports multi-turn conversations with system prompts.
    
    Example:
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How do I book a ticket?"}
        ]
    }
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model is still loading. Please try again in a moment.")
    
    try:
        # Convert Pydantic models to dict format for tokenizer
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Add system prompt if not present
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
        # Apply chat template
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(model.device)
        
        # Generate response
        max_tokens = request.max_tokens or MAX_NEW_TOKENS
        temp = request.temperature or TEMPERATURE
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temp,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Decode only the new tokens (response)
        response_text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        ).strip()
        
        return ChatResponse(
            response=response_text,
            model=MODEL_NAME,
            tokens_used=outputs.shape[-1] - inputs["input_ids"].shape[-1]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation error: {str(e)}")

@app.post("/ask", response_model=QuestionResponse, tags=["faq"])
async def ask_question(request: QuestionRequest):
    """
    Simple Q&A endpoint for single questions.
    Automatically includes movie booking system context.
    
    Example:
    {
        "question": "How do I cancel my booking?"
    }
    """
    if text_gen_pipeline is None:
        raise HTTPException(status_code=503, detail="Model is still loading. Please try again in a moment.")
    
    try:
        # Create a simple conversation with system context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.question}
        ]
        
        # Use pipeline for simpler generation
        result = text_gen_pipeline(
            messages,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            return_full_text=False
        )
        
        # Extract the assistant's response
        answer = result[0]["generated_text"].strip()
        
        return QuestionResponse(
            answer=answer,
            question=request.question,
            model=MODEL_NAME
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering error: {str(e)}")
