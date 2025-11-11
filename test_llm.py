#!/usr/bin/env python3
"""
Test script for the LLM Server
Tests both /ask and /chat endpoints
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8500"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Service: {data.get('service')}")
        print(f"✅ Model: {data.get('model')}")
        print(f"✅ Model Loaded: {data.get('model_loaded')}")
        print(f"✅ Device: {data.get('device')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_ask(question):
    """Test the /ask endpoint"""
    print_section(f"Testing /ask endpoint")
    print(f"Question: {question}\n")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=30
        )
        duration = time.time() - start_time
        
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response time: {duration:.2f}s")
        print(f"\n📝 Answer:\n{data.get('answer')}\n")
        return True
    except Exception as e:
        print(f"❌ Ask endpoint failed: {e}")
        return False

def test_chat(messages):
    """Test the /chat endpoint"""
    print_section("Testing /chat endpoint")
    
    for msg in messages:
        print(f"{msg['role'].upper()}: {msg['content']}")
    print()
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"messages": messages},
            timeout=30
        )
        duration = time.time() - start_time
        
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response time: {duration:.2f}s")
        print(f"✅ Tokens used: {data.get('tokens_used')}")
        print(f"\n🤖 Assistant:\n{data.get('response')}\n")
        return True
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False

def test_multi_turn_chat():
    """Test multi-turn conversation"""
    print_section("Testing Multi-Turn Conversation")
    
    messages = [
        {"role": "user", "content": "How do I book a movie ticket?"}
    ]
    
    # First turn
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"messages": messages},
            timeout=30
        )
        data = response.json()
        assistant_msg = data.get('response')
        
        print(f"USER: {messages[0]['content']}")
        print(f"ASSISTANT: {assistant_msg}\n")
        
        # Second turn
        messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": "What if I want to cancel it later?"})
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"messages": messages},
            timeout=30
        )
        data = response.json()
        
        print(f"USER: {messages[-1]['content']}")
        print(f"ASSISTANT: {data.get('response')}\n")
        
        print("✅ Multi-turn conversation successful")
        return True
    except Exception as e:
        print(f"❌ Multi-turn chat failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🤖 LLM Server Test Suite")
    print(f"Testing server at: {BASE_URL}")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n❌ Server not ready. Please start the LLM server first:")
        print("   docker-compose up -d llm-server")
        print("   OR")
        print("   python -m uvicorn llm.llm_server:app --host 0.0.0.0 --port 8500")
        sys.exit(1)
    
    # Wait a moment for model to be ready
    time.sleep(2)
    
    # Test 2: Simple FAQ
    results.append((
        "Simple FAQ",
        test_ask("How do I cancel my booking?")
    ))
    
    # Test 3: System question
    results.append((
        "System Question",
        test_ask("What is the Raft consensus protocol?")
    ))
    
    # Test 4: Single turn chat
    results.append((
        "Single Turn Chat",
        test_chat([
            {"role": "user", "content": "I want to book tickets for a movie"}
        ])
    ))
    
    # Test 5: Multi-turn conversation
    results.append((
        "Multi-Turn Chat",
        test_multi_turn_chat()
    ))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
