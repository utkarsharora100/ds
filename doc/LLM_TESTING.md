# 🤖 LLM Server Testing Guide

This guide shows how to test the new Qwen2.5-0.5B powered LLM server.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Start only the LLM server
docker-compose up -d llm-server

# Watch logs
docker-compose logs -f llm-server
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Load environment variables
export LLM_MODEL=Qwen/Qwen2.5-0.5B
export LLM_MAX_NEW_TOKENS=512
export LLM_TEMPERATURE=0.7

# Start server
python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500 --reload
```

---

## 📊 API Endpoints

### 1. Health Check

```bash
curl http://localhost:8500/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "llm-server",
  "model": "Qwen/Qwen2.5-0.5B",
  "model_loaded": true,
  "device": "cpu"
}
```

---

### 2. Simple Question/Answer (FAQ Mode)

**Endpoint:** `POST /ask`

```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I cancel my booking?"
  }'
```

**Response:**
```json
{
  "answer": "You can cancel your booking up to 1 hour before the showtime. Refunds are processed within 3-5 business days. Please use the cancellation option in your booking confirmation or contact support@movietix.ai for assistance.",
  "question": "How do I cancel my booking?",
  "model": "Qwen/Qwen2.5-0.5B"
}
```

**More Examples:**

```bash
# About payment
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What happens if my payment fails?"}'

# About system architecture
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How does the Raft consensus protocol work in this system?"}'

# About availability
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How can I check seat availability?"}'
```

---

### 3. Chat Mode (Conversational)

**Endpoint:** `POST /chat`

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I want to book tickets for a movie"
      }
    ]
  }'
```

**Response:**
```json
{
  "response": "I'd be happy to help you book movie tickets! To get started, I'll need some information:\n\n1. Which movie would you like to watch?\n2. What date and time works for you?\n3. How many seats do you need?\n4. Which city are you in?\n\nOnce you provide these details, I can help you check availability and complete your booking.",
  "model": "Qwen/Qwen2.5-0.5B",
  "tokens_used": 87
}
```

---

### 4. Multi-Turn Conversation

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I want to book tickets"
      },
      {
        "role": "assistant",
        "content": "I can help you with that. Which movie would you like to watch?"
      },
      {
        "role": "user",
        "content": "Inception, tomorrow evening"
      }
    ]
  }'
```

---

### 5. Custom System Prompt

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a concise movie booking assistant. Keep responses under 50 words."
      },
      {
        "role": "user",
        "content": "How do I book a ticket?"
      }
    ]
  }'
```

---

### 6. Adjust Generation Parameters

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Tell me about the booking process"
      }
    ],
    "max_tokens": 100,
    "temperature": 0.5
  }'
```

**Parameters:**
- `max_tokens`: Maximum length of response (default: 512)
- `temperature`: Creativity/randomness (0.1-1.0, default: 0.7)
  - Lower = more focused and deterministic
  - Higher = more creative and diverse

---

## 🐍 Python Examples

### Simple Question

```python
import requests

url = "http://localhost:8500/ask"
data = {
    "question": "What are the cancellation rules?"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Q: {result['question']}")
print(f"A: {result['answer']}")
```

---

### Chat Conversation

```python
import requests

url = "http://localhost:8500/chat"

# Start conversation
messages = [
    {"role": "user", "content": "I need help booking a movie ticket"}
]

response = requests.post(url, json={"messages": messages})
assistant_reply = response.json()["response"]

print(f"Assistant: {assistant_reply}")

# Continue conversation
messages.append({"role": "assistant", "content": assistant_reply})
messages.append({"role": "user", "content": "What movies are available?"})

response = requests.post(url, json={"messages": messages})
print(f"Assistant: {response.json()['response']}")
```

---

### Full Booking Assistant Script

```python
import requests

class BookingAssistant:
    def __init__(self, base_url="http://localhost:8500"):
        self.base_url = base_url
        self.messages = []
    
    def ask(self, question):
        """Quick FAQ-style question"""
        response = requests.post(
            f"{self.base_url}/ask",
            json={"question": question}
        )
        return response.json()["answer"]
    
    def chat(self, user_message):
        """Conversational chat"""
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        response = requests.post(
            f"{self.base_url}/chat",
            json={"messages": self.messages}
        )
        
        assistant_message = response.json()["response"]
        
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def reset(self):
        """Reset conversation"""
        self.messages = []

# Usage
assistant = BookingAssistant()

# FAQ mode
answer = assistant.ask("How long does a refund take?")
print(f"Quick Answer: {answer}")

# Chat mode
response1 = assistant.chat("I want to book a movie")
print(f"Bot: {response1}")

response2 = assistant.chat("Which movies are playing this weekend?")
print(f"Bot: {response2}")

# Reset and start new conversation
assistant.reset()
```

---

## 🧪 Performance Testing

### Load Test Script

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def test_request():
    start = time.time()
    response = requests.post(
        "http://localhost:8500/ask",
        json={"question": "How do I book a ticket?"}
    )
    duration = time.time() - start
    return response.status_code, duration

# Run 10 concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: test_request(), range(10)))

# Print results
for i, (status, duration) in enumerate(results, 1):
    print(f"Request {i}: {status} - {duration:.2f}s")

avg_time = sum(d for _, d in results) / len(results)
print(f"\nAverage response time: {avg_time:.2f}s")
```

---

## 📊 Expected Performance

### Model: Qwen/Qwen2.5-0.5B

| Metric | Value |
|--------|-------|
| Model Size | ~500MB |
| Parameters | 500M |
| Initial Load Time | 30-60 seconds |
| Response Time (CPU) | 2-5 seconds |
| Response Time (GPU) | 0.5-1 second |
| Memory Usage | 2-4GB |
| Max Context Length | 32K tokens |

---

## 🔍 Troubleshooting

### Issue: Model Not Loading

**Check logs:**
```bash
docker-compose logs llm-server
```

**Common causes:**
- Insufficient memory (need 2GB+)
- Network issues downloading model
- Missing dependencies

**Solution:**
```bash
# Rebuild with fresh dependencies
docker-compose build --no-cache llm-server
docker-compose up -d llm-server
```

---

### Issue: Slow Responses

**CPU Mode is Slower:**
- Expected: 2-5 seconds per response
- GPU would be: 0.5-1 second

**Optimize:**
1. Reduce `max_tokens` in requests
2. Lower `temperature` for faster generation
3. Use `/ask` endpoint instead of `/chat` for simple queries

---

### Issue: Out of Memory

**Error:** Container crashes or restarts

**Solution:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 6G
```

Or run without LLM:
```bash
docker-compose up -d app-server raft-node1 raft-node2 raft-node3
```

---

## 🎯 Integration Examples

### Use in Application Server

```python
import requests

def get_ai_response(user_question):
    """Get AI response from LLM server"""
    try:
        response = requests.post(
            "http://llm-server:8500/ask",  # Use container name in Docker
            json={"question": user_question},
            timeout=10
        )
        return response.json()["answer"]
    except Exception as e:
        return "Sorry, I couldn't process your question right now."
```

---

### Use in Client App

```python
# In client/client.py
class Client:
    def ask_support(self, question):
        """Ask the AI support assistant"""
        response = requests.post(
            f"{APP_SERVER_URL}/llm/ask",
            json={"question": question}
        )
        return response.json()["answer"]
```

---

## 📈 Model Comparison

| Feature | Old (RoBERTa Q&A) | New (Qwen2.5-0.5B) |
|---------|-------------------|---------------------|
| Type | Extractive Q&A | Generative Chat |
| Size | 125M params | 500M params |
| Context | Fixed FAQ | Full conversation |
| Response Type | Extracts from text | Generates new text |
| Flexibility | Low | High |
| Quality | Good for FAQs | Better overall |

---

## 🚀 Next Steps

1. **Test the endpoints** using curl or Python
2. **Monitor performance** with the load test script
3. **Integrate with your app** using the examples above
4. **Customize system prompt** for better responses
5. **Adjust parameters** (temperature, max_tokens) as needed

---

**Ready to test!** 🎉

Start with a simple health check:
```bash
curl http://localhost:8500/health
```

Then try asking a question:
```bash
curl -X POST http://localhost:8500/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How does the booking system work?"}'
```
