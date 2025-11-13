#!/usr/bin/env python3
"""
LLM Performance Benchmarking Script
Tests response times, concurrent load, cache effects, and memory usage
"""

import requests
import time
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

# Configuration
LLM_URL = "http://localhost:8500"
ASK_ENDPOINT = f"{LLM_URL}/ask"
HEALTH_ENDPOINT = f"{LLM_URL}/health"

# Benchmark test questions
BENCHMARK_QUESTIONS = [
    "How do I book a ticket?",
    "What is the cancellation policy?",
    "How do I contact support?",
    "What is Raft consensus?",
    "Can I select specific seats?",
]


class LLMBenchmark:
    def __init__(self):
        self.results = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "distilgpt2",
            "benchmarks": {}
        }

    def check_health(self) -> bool:
        """Check if LLM server is healthy"""
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LLM Server: {data.get('status')}")
                print(f"   Model: {data.get('model')}")
                print(f"   Device: {data.get('device')}")
                return data.get('model_loaded', False)
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def ask_question(self, question: str, timeout: int = 30) -> Tuple[str, float, bool]:
        """Ask a single question and measure response time"""
        try:
            start_time = time.time()
            response = requests.post(
                ASK_ENDPOINT,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                return answer, response_time, True
            else:
                return f"Error: {response.status_code}", response_time, False

        except requests.Timeout:
            return "Error: Timeout", timeout, False
        except Exception as e:
            return f"Error: {str(e)}", 0.0, False

    def benchmark_sequential(self, iterations: int = 10) -> Dict:
        """Benchmark sequential requests"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK 1: Sequential Requests ({iterations} iterations)")
        print(f"{'='*70}\n")

        times = []
        success_count = 0

        for i, question in enumerate(BENCHMARK_QUESTIONS * (iterations // len(BENCHMARK_QUESTIONS) + 1), 1):
            if i > iterations:
                break

            print(f"[{i}/{iterations}] Testing: {question[:50]}...")
            answer, response_time, success = self.ask_question(question)

            if success:
                times.append(response_time)
                success_count += 1
                print(f"            ✓ {response_time:.2f}s")
            else:
                print(f"            ✗ Failed: {answer}")

        if times:
            results = {
                "iterations": iterations,
                "successful": success_count,
                "failed": iterations - success_count,
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "min_time": min(times),
                "max_time": max(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "all_times": times
            }

            print(f"\n📊 Results:")
            print(f"   Average: {results['avg_time']:.2f}s")
            print(f"   Median:  {results['median_time']:.2f}s")
            print(f"   Min/Max: {results['min_time']:.2f}s / {results['max_time']:.2f}s")
            print(f"   StdDev:  {results['stdev']:.2f}s")
            print(f"   Success: {success_count}/{iterations}")

            return results
        else:
            return {"error": "All requests failed"}

    def benchmark_concurrent(self, num_requests: int = 10, num_workers: int = 5) -> Dict:
        """Benchmark concurrent requests (simulating multiple users)"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK 2: Concurrent Requests ({num_requests} requests, {num_workers} workers)")
        print(f"{'='*70}\n")

        questions = BENCHMARK_QUESTIONS * (num_requests // len(BENCHMARK_QUESTIONS) + 1)
        questions = questions[:num_requests]

        times = []
        success_count = 0
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit all requests
            futures = {executor.submit(self.ask_question, q): i for i, q in enumerate(questions, 1)}

            # Collect results
            for future in as_completed(futures):
                req_num = futures[future]
                try:
                    answer, response_time, success = future.result()
                    if success:
                        times.append(response_time)
                        success_count += 1
                        print(f"[{req_num}/{num_requests}] ✓ {response_time:.2f}s")
                    else:
                        print(f"[{req_num}/{num_requests}] ✗ Failed: {answer}")
                except Exception as e:
                    print(f"[{req_num}/{num_requests}] ✗ Exception: {e}")

        total_time = time.time() - start_time

        if times:
            results = {
                "num_requests": num_requests,
                "num_workers": num_workers,
                "successful": success_count,
                "failed": num_requests - success_count,
                "total_time": total_time,
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "min_time": min(times),
                "max_time": max(times),
                "throughput": num_requests / total_time,
                "all_times": times
            }

            print(f"\n📊 Results:")
            print(f"   Total time:  {results['total_time']:.2f}s")
            print(f"   Average:     {results['avg_time']:.2f}s")
            print(f"   Median:      {results['median_time']:.2f}s")
            print(f"   Min/Max:     {results['min_time']:.2f}s / {results['max_time']:.2f}s")
            print(f"   Throughput:  {results['throughput']:.2f} req/s")
            print(f"   Success:     {success_count}/{num_requests}")

            return results
        else:
            return {"error": "All requests failed"}

    def benchmark_warmup_effect(self, iterations: int = 5) -> Dict:
        """Test if there's a cache warmup effect (first request vs subsequent)"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK 3: Cache Warmup Effect ({iterations} rounds)")
        print(f"{'='*70}\n")

        question = "How do I book a ticket?"
        first_request_times = []
        subsequent_times = []

        for round_num in range(1, iterations + 1):
            print(f"\nRound {round_num}/{iterations}")

            # Pause to let model "cool down"
            time.sleep(2)

            # First request
            print(f"  First request...")
            _, first_time, success1 = self.ask_question(question)
            if success1:
                first_request_times.append(first_time)
                print(f"    ✓ {first_time:.2f}s")

            # Subsequent requests
            times = []
            for i in range(3):
                _, sub_time, success2 = self.ask_question(question)
                if success2:
                    times.append(sub_time)
            if times:
                avg_sub = statistics.mean(times)
                subsequent_times.append(avg_sub)
                print(f"  Subsequent (avg of 3): {avg_sub:.2f}s")

        if first_request_times and subsequent_times:
            results = {
                "iterations": iterations,
                "first_avg": statistics.mean(first_request_times),
                "subsequent_avg": statistics.mean(subsequent_times),
                "difference": statistics.mean(first_request_times) - statistics.mean(subsequent_times),
                "first_times": first_request_times,
                "subsequent_times": subsequent_times
            }

            print(f"\n📊 Results:")
            print(f"   First request avg:      {results['first_avg']:.2f}s")
            print(f"   Subsequent requests avg: {results['subsequent_avg']:.2f}s")
            print(f"   Difference:             {results['difference']:.2f}s")

            if abs(results['difference']) > 0.5:
                print(f"   ⚠️  Significant warmup effect detected!")
            else:
                print(f"   ✅ No significant warmup effect")

            return results
        else:
            return {"error": "Insufficient data"}

    def benchmark_memory_usage(self) -> Dict:
        """Check memory usage (requires docker stats)"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK 4: Memory Usage")
        print(f"{'='*70}\n")

        try:
            import subprocess

            # Get memory usage from docker stats
            cmd = ["docker", "stats", "movie-llm-server", "--no-stream", "--format", "{{.MemUsage}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                mem_usage = result.stdout.strip()
                print(f"   Memory usage: {mem_usage}")
                return {"memory_usage": mem_usage}
            else:
                print(f"   ⚠️  Could not retrieve memory stats")
                print(f"   Note: Requires Docker to be running")
                return {"error": "Docker stats unavailable"}

        except subprocess.TimeoutExpired:
            return {"error": "Docker command timeout"}
        except FileNotFoundError:
            print(f"   ⚠️  Docker command not found")
            print(f"   Note: This benchmark requires Docker CLI")
            return {"error": "Docker not available"}
        except Exception as e:
            return {"error": str(e)}

    def benchmark_response_consistency(self, iterations: int = 5) -> Dict:
        """Test if same question gets consistent responses"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK 5: Response Consistency ({iterations} iterations)")
        print(f"{'='*70}\n")

        question = "What is the refund policy?"
        responses = []
        times = []

        print(f"Question: {question}\n")

        for i in range(1, iterations + 1):
            answer, response_time, success = self.ask_question(question)
            if success:
                responses.append(answer)
                times.append(response_time)
                print(f"[{i}] {response_time:.2f}s - {answer[:80]}...")
            else:
                print(f"[{i}] Failed: {answer}")

        if len(responses) >= 2:
            # Compare responses (simple similarity check)
            unique_responses = set(responses)
            similarity = 1.0 - (len(unique_responses) / len(responses))

            results = {
                "iterations": iterations,
                "unique_responses": len(unique_responses),
                "similarity": similarity,
                "avg_time": statistics.mean(times),
                "responses": responses
            }

            print(f"\n📊 Results:")
            print(f"   Unique responses: {len(unique_responses)}/{len(responses)}")
            print(f"   Similarity:       {similarity*100:.1f}%")
            print(f"   Avg time:         {results['avg_time']:.2f}s")

            if similarity > 0.8:
                print(f"   ✅ High consistency (deterministic responses)")
            elif similarity > 0.5:
                print(f"   ⚠️  Moderate consistency (some variation)")
            else:
                print(f"   ⚠️  Low consistency (highly variable)")

            return results
        else:
            return {"error": "Insufficient successful responses"}

    def generate_summary(self):
        """Generate overall benchmark summary"""
        print(f"\n{'='*70}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*70}\n")

        # Sequential performance
        if "sequential" in self.results["benchmarks"]:
            seq = self.results["benchmarks"]["sequential"]
            print(f"📈 Sequential Performance:")
            print(f"   Average: {seq.get('avg_time', 'N/A'):.2f}s")
            print(f"   Median:  {seq.get('median_time', 'N/A'):.2f}s")

            avg_time = seq.get('avg_time', 0)
            if avg_time <= 3:
                print(f"   ✅ Excellent (<3s)")
            elif avg_time <= 5:
                print(f"   ✅ Good (3-5s)")
            else:
                print(f"   ⚠️  Needs improvement (>5s)")

        # Concurrent performance
        if "concurrent" in self.results["benchmarks"]:
            conc = self.results["benchmarks"]["concurrent"]
            print(f"\n🔀 Concurrent Performance:")
            print(f"   Throughput:  {conc.get('throughput', 0):.2f} req/s")
            print(f"   Success rate: {conc.get('successful', 0)}/{conc.get('num_requests', 0)}")

        # Warmup effect
        if "warmup" in self.results["benchmarks"]:
            warmup = self.results["benchmarks"]["warmup"]
            if "difference" in warmup:
                if abs(warmup['difference']) > 0.5:
                    print(f"\n⚠️  Warmup Effect: {warmup['difference']:.2f}s slower on first request")
                else:
                    print(f"\n✅ No significant warmup effect")

        # Memory
        if "memory" in self.results["benchmarks"]:
            mem = self.results["benchmarks"]["memory"]
            if "memory_usage" in mem:
                print(f"\n💾 Memory Usage: {mem['memory_usage']}")

        # Consistency
        if "consistency" in self.results["benchmarks"]:
            cons = self.results["benchmarks"]["consistency"]
            if "similarity" in cons:
                print(f"\n🎯 Response Consistency: {cons['similarity']*100:.1f}%")

        print(f"\n{'='*70}")
        print(f"✅ BENCHMARKING COMPLETE")
        print(f"{'='*70}\n")

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        filepath = f"/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds/tests/{filename}"
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Results saved to: {filename}")


def main():
    """Run all benchmarks"""
    print(f"{'='*70}")
    print(f"LLM PERFORMANCE BENCHMARKING")
    print(f"DistilGPT-2 Movie Booking Assistant")
    print(f"{'='*70}")

    benchmark = LLMBenchmark()

    # Check health
    if not benchmark.check_health():
        print("\n❌ LLM server not ready. Please start and try again.")
        print("   Run: docker compose -f docker-compose.combined.yml up -d llm-server")
        return

    print("\n✅ Starting benchmarks...\n")

    try:
        # Run all benchmarks
        benchmark.results["benchmarks"]["sequential"] = benchmark.benchmark_sequential(iterations=10)
        benchmark.results["benchmarks"]["concurrent"] = benchmark.benchmark_concurrent(num_requests=10, num_workers=5)
        benchmark.results["benchmarks"]["warmup"] = benchmark.benchmark_warmup_effect(iterations=3)
        benchmark.results["benchmarks"]["memory"] = benchmark.benchmark_memory_usage()
        benchmark.results["benchmarks"]["consistency"] = benchmark.benchmark_response_consistency(iterations=5)

        # Generate summary
        benchmark.generate_summary()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        benchmark.save_results(f"benchmark_results_{timestamp}.json")

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmarks interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during benchmarking: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
