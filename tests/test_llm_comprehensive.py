#!/usr/bin/env python3
"""
Comprehensive LLM Test Suite for DistilGPT-2 Movie Booking Assistant
Tests response quality, performance, and edge case handling
"""

import requests
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime

# LLM Server Configuration
LLM_URL = "http://localhost:8500"
ASK_ENDPOINT = f"{LLM_URL}/ask"
HEALTH_ENDPOINT = f"{LLM_URL}/health"

# Test Categories
FAQ_QUESTIONS = [
    # Booking Process
    ("How do I book a ticket?", "booking", True),
    ("What payment methods are accepted?", "payment", True),
    ("Can I select specific seats?", "seats", True),
    ("How do I know if my booking is confirmed?", "confirmation", True),

    # Cancellation & Refunds
    ("How do I cancel my booking?", "cancellation", True),
    ("What is the cancellation policy?", "policy", True),
    ("When will I get my refund?", "refund", True),
    ("Can I cancel 30 minutes before showtime?", "cancellation_timing", True),

    # System Information
    ("What is Raft consensus?", "raft", True),
    ("How does the system handle failures?", "fault_tolerance", True),
    ("What happens if a node crashes?", "node_failure", True),
    ("How is data consistency maintained?", "consistency", True),

    # Seat Availability
    ("How do I check seat availability?", "availability", True),
    ("What if seats are full?", "full_seats", True),
    ("Can I book multiple tickets?", "multiple_booking", True),

    # Support & Contact
    ("How do I contact support?", "support", True),
    ("What are your business hours?", "hours", False),  # May not be in system prompt
]

EDGE_CASES = [
    # Ambiguous questions
    ("Can I?", "ambiguous", False),
    ("What about it?", "ambiguous", False),
    ("Help", "ambiguous", True),  # Should provide general help

    # Very long questions
    ("I want to book a ticket for a movie but I'm not sure which movie to watch and I also want to know if I can cancel the booking later if I change my mind and also what is the refund policy and how long does it take to process the refund?", "long_question", True),

    # Technical/Complex questions
    ("Explain the Raft leader election algorithm in detail", "technical_detail", True),
    ("How does two-phase commit work?", "technical_advanced", False),

    # Off-topic questions
    ("What's the weather today?", "off_topic", False),
    ("Who won the Oscar?", "off_topic", False),
    ("Tell me a joke", "off_topic", False),
    ("What's the capital of France?", "off_topic", False),

    # Empty/whitespace
    ("", "empty", False),
    ("   ", "whitespace", False),

    # Repeated words
    ("book book book ticket ticket", "repeated", True),

    # Special characters
    ("How do I book??? @#$%", "special_chars", True),
]

FOLLOW_UP_QUESTIONS = [
    # Context-dependent questions
    ("What about refunds?", "context_dependent", False),
    ("And then what?", "context_dependent", False),
]


class LLMTester:
    def __init__(self):
        self.results = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "distilgpt2",
            "faq_results": [],
            "edge_case_results": [],
            "performance_metrics": {
                "response_times": [],
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
            },
            "quality_metrics": {
                "on_topic_count": 0,
                "off_topic_count": 0,
                "relevant_responses": 0,
                "irrelevant_responses": 0,
                "empty_responses": 0,
                "repetitive_responses": 0,
            }
        }

    def check_health(self) -> bool:
        """Check if LLM server is healthy"""
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LLM Server Health: {data.get('status')}")
                print(f"   Model: {data.get('model')}")
                print(f"   Model Loaded: {data.get('model_loaded')}")
                return data.get('model_loaded', False)
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def ask_question(self, question: str) -> Tuple[str, float, bool]:
        """
        Ask a question to the LLM
        Returns: (answer, response_time, success)
        """
        try:
            start_time = time.time()
            response = requests.post(
                ASK_ENDPOINT,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                return answer, response_time, True
            else:
                return f"Error: {response.status_code}", response_time, False

        except requests.Timeout:
            return "Error: Request timeout", 30.0, False
        except Exception as e:
            return f"Error: {str(e)}", 0.0, False

    def evaluate_response(self, question: str, answer: str, category: str, should_answer: bool) -> Dict:
        """
        Evaluate response quality
        Returns metrics about the response
        """
        metrics = {
            "question": question,
            "answer": answer,
            "category": category,
            "should_answer": should_answer,
            "answer_length": len(answer),
            "is_empty": len(answer.strip()) == 0,
            "is_error": answer.startswith("Error:"),
            "contains_system_info": False,
            "is_repetitive": False,
            "is_on_topic": False,
        }

        # Check if answer is empty
        if metrics["is_empty"]:
            self.results["quality_metrics"]["empty_responses"] += 1
            return metrics

        # Check for repetition (same phrase repeated 3+ times)
        words = answer.lower().split()
        if len(words) > 3:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            max_repeat = max(word_counts.values())
            if max_repeat >= 3:
                metrics["is_repetitive"] = True
                self.results["quality_metrics"]["repetitive_responses"] += 1

        # Check for system-specific keywords
        system_keywords = [
            "raft", "consensus", "leader", "node", "booking", "ticket",
            "cancel", "refund", "payment", "seat", "showtime", "movie",
            "support@movietix", "3-5 business days", "1 hour before"
        ]
        answer_lower = answer.lower()
        keywords_found = sum(1 for keyword in system_keywords if keyword in answer_lower)
        if keywords_found >= 2:
            metrics["contains_system_info"] = True

        # Determine if response is on-topic
        if should_answer:
            # Should provide relevant answer
            if not metrics["is_error"] and not metrics["is_empty"]:
                # Check if answer seems related to question
                question_words = set(question.lower().split())
                answer_words = set(answer_lower.split())
                common_words = question_words & answer_words

                if len(common_words) >= 2 or metrics["contains_system_info"]:
                    metrics["is_on_topic"] = True
                    self.results["quality_metrics"]["relevant_responses"] += 1
                else:
                    self.results["quality_metrics"]["irrelevant_responses"] += 1
        else:
            # Off-topic or invalid question - should handle gracefully
            if "sorry" in answer_lower or "can't" in answer_lower or "cannot" in answer_lower:
                metrics["is_on_topic"] = True  # Correctly handled off-topic
                self.results["quality_metrics"]["relevant_responses"] += 1

        return metrics

    def test_faq_questions(self):
        """Test all FAQ questions"""
        print("\n" + "="*70)
        print("TESTING FAQ QUESTIONS")
        print("="*70 + "\n")

        for question, category, should_answer in FAQ_QUESTIONS:
            print(f"\n📝 Q: {question}")

            answer, response_time, success = self.ask_question(question)

            if success:
                print(f"⏱️  Response time: {response_time:.2f}s")
                print(f"💬 A: {answer[:200]}{'...' if len(answer) > 200 else ''}")

                # Evaluate response
                metrics = self.evaluate_response(question, answer, category, should_answer)
                metrics["response_time"] = response_time
                self.results["faq_results"].append(metrics)
                self.results["performance_metrics"]["response_times"].append(response_time)
                self.results["performance_metrics"]["successful_tests"] += 1

                # Quick feedback
                if metrics["is_on_topic"]:
                    print("✅ On-topic response")
                if metrics["contains_system_info"]:
                    print("✅ Uses system knowledge")
                if metrics["is_repetitive"]:
                    print("⚠️  Repetitive content detected")
            else:
                print(f"❌ Failed: {answer}")
                self.results["performance_metrics"]["failed_tests"] += 1

            self.results["performance_metrics"]["total_tests"] += 1
            time.sleep(0.5)  # Brief pause between requests

    def test_edge_cases(self):
        """Test edge cases"""
        print("\n" + "="*70)
        print("TESTING EDGE CASES")
        print("="*70 + "\n")

        for question, category, should_handle in EDGE_CASES:
            display_q = question if question else "[empty string]"
            print(f"\n📝 Q [{category}]: {display_q[:100]}")

            answer, response_time, success = self.ask_question(question)

            if success:
                print(f"⏱️  Response time: {response_time:.2f}s")
                print(f"💬 A: {answer[:150]}{'...' if len(answer) > 150 else ''}")

                # Evaluate response
                metrics = self.evaluate_response(question, answer, category, should_handle)
                metrics["response_time"] = response_time
                metrics["should_handle"] = should_handle
                self.results["edge_case_results"].append(metrics)
                self.results["performance_metrics"]["response_times"].append(response_time)
                self.results["performance_metrics"]["successful_tests"] += 1

                # Quick feedback
                if should_handle and metrics["is_on_topic"]:
                    print("✅ Handled gracefully")
                elif not should_handle and not metrics["is_error"]:
                    print("⚠️  Should have detected as off-topic/invalid")
            else:
                print(f"❌ Failed: {answer}")
                self.results["performance_metrics"]["failed_tests"] += 1

            self.results["performance_metrics"]["total_tests"] += 1
            time.sleep(0.5)

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("TEST REPORT SUMMARY")
        print("="*70 + "\n")

        # Performance metrics
        response_times = self.results["performance_metrics"]["response_times"]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            print("⏱️  PERFORMANCE METRICS:")
            print(f"   Average response time: {avg_time:.2f}s")
            print(f"   Min/Max response time: {min_time:.2f}s / {max_time:.2f}s")
            print(f"   Total tests: {self.results['performance_metrics']['total_tests']}")
            print(f"   Successful: {self.results['performance_metrics']['successful_tests']}")
            print(f"   Failed: {self.results['performance_metrics']['failed_tests']}")

            # Performance rating
            if avg_time <= 3:
                print("   ✅ Excellent performance (<3s average)")
            elif avg_time <= 5:
                print("   ✅ Good performance (3-5s average)")
            else:
                print("   ⚠️  Slow performance (>5s average)")

        # Quality metrics
        print("\n📊 QUALITY METRICS:")
        q = self.results["quality_metrics"]
        print(f"   Relevant responses: {q['relevant_responses']}")
        print(f"   Irrelevant responses: {q['irrelevant_responses']}")
        print(f"   Empty responses: {q['empty_responses']}")
        print(f"   Repetitive responses: {q['repetitive_responses']}")

        total_responses = q['relevant_responses'] + q['irrelevant_responses']
        if total_responses > 0:
            relevance_rate = (q['relevant_responses'] / total_responses) * 100
            print(f"   Relevance rate: {relevance_rate:.1f}%")

            if relevance_rate >= 80:
                print("   ✅ Excellent relevance (≥80%)")
            elif relevance_rate >= 60:
                print("   ⚠️  Moderate relevance (60-80%)")
            else:
                print("   ❌ Low relevance (<60%)")

        # FAQ results
        print(f"\n📋 FAQ QUESTIONS: {len(self.results['faq_results'])} tested")
        faq_with_system_info = sum(1 for r in self.results['faq_results'] if r['contains_system_info'])
        faq_on_topic = sum(1 for r in self.results['faq_results'] if r['is_on_topic'])
        print(f"   Uses system knowledge: {faq_with_system_info}/{len(self.results['faq_results'])}")
        print(f"   On-topic responses: {faq_on_topic}/{len(self.results['faq_results'])}")

        # Edge case results
        print(f"\n⚠️  EDGE CASES: {len(self.results['edge_case_results'])} tested")
        edge_handled = sum(1 for r in self.results['edge_case_results']
                          if r['should_handle'] and r['is_on_topic'])
        edge_should_handle = sum(1 for r in self.results['edge_case_results'] if r['should_handle'])
        if edge_should_handle > 0:
            print(f"   Handled gracefully: {edge_handled}/{edge_should_handle}")

        # Key weaknesses
        print("\n🔍 KEY WEAKNESSES IDENTIFIED:")
        weaknesses = []

        if faq_with_system_info < len(self.results['faq_results']) * 0.5:
            weaknesses.append("   ❌ Not using system knowledge (SYSTEM_PROMPT not injected)")

        if q['irrelevant_responses'] > q['relevant_responses'] * 0.3:
            weaknesses.append("   ❌ Many irrelevant responses (>30% off-topic)")

        if q['empty_responses'] > 0:
            weaknesses.append(f"   ❌ {q['empty_responses']} empty responses generated")

        if q['repetitive_responses'] > 0:
            weaknesses.append(f"   ⚠️  {q['repetitive_responses']} repetitive responses")

        if avg_time > 5:
            weaknesses.append("   ⚠️  Slow response times (>5s average)")

        if weaknesses:
            for weakness in weaknesses:
                print(weakness)
        else:
            print("   ✅ No major weaknesses detected!")

        # Improvement recommendations
        print("\n💡 IMPROVEMENT OPPORTUNITIES:")
        print("   1. Add few-shot examples to prompt (teach response style)")
        print("   2. Inject system context (movie booking info)")
        print("   3. Implement fallback for common questions (template responses)")
        print("   4. Add off-topic detection (filter weather/sports questions)")
        print("   5. Optimize generation parameters (reduce temperature for FAQ)")

        return self.results

    def save_results(self, filename: str = "test_results.json"):
        """Save detailed results to JSON file"""
        filepath = f"/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds/tests/{filename}"
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {filename}")


def main():
    """Run comprehensive LLM tests"""
    print("="*70)
    print("COMPREHENSIVE LLM TEST SUITE")
    print("DistilGPT-2 Movie Booking Assistant")
    print("="*70)

    tester = LLMTester()

    # Check health
    if not tester.check_health():
        print("\n❌ LLM server not ready. Please start the server and try again.")
        print("   Run: docker compose -f docker-compose.combined.yml up -d llm-server")
        return

    print("\n✅ LLM server is ready. Starting tests...\n")

    # Run tests
    try:
        tester.test_faq_questions()
        tester.test_edge_cases()

        # Generate report
        results = tester.generate_report()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tester.save_results(f"test_results_{timestamp}.json")

        print("\n" + "="*70)
        print("✅ TESTING COMPLETE!")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
