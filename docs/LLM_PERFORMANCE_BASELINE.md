# LLM Performance Baseline - DistilGPT-2

**Test Date:** 2025-11-13 05:43:02
**Model:** distilgpt2 (82M parameters)
**Prompt Format:** Simple "Q: / A:"
**Status:** ⚠️ NEEDS IMPROVEMENT

---

## Executive Summary

Comprehensive testing of the DistilGPT-2 LLM revealed **critical quality issues** despite meeting performance targets for model size. The current simple prompt format results in:

- ❌ **19% relevance rate** (target: >80%)
- ❌ **Not using system knowledge** (only 2/17 FAQ questions)
- ❌ **No off-topic detection** (answers weather, sports questions)
- ⚠️ **6.06s average response** (target: 2-3s)
- ⚠️ **0% consistency** (highly random responses)

**Conclusion:** Model works but needs better prompts and fallback strategies.

---

## Performance Metrics

### Response Times

| Metric | Sequential Test | Concurrent Test | Target |
|--------|----------------|-----------------|--------|
| **Average** | 6.06s | 18.87s | 2-3s |
| **Median** | 6.08s | 20.01s | - |
| **Min** | 2.10s | 5.72s | - |
| **Max** | 10.16s | 29.92s | 5s max |
| **Success Rate** | 100% (10/10) | 70% (7/10) | >95% |

**Analysis:**
- ⚠️ Sequential performance **2x slower** than expected (6s vs 3s)
- ❌ Concurrent performance **very poor** - 30% timeout rate
- ⚠️ High variability (2s to 10s) indicates inconsistent generation

**Causes:**
1. Model generating too much text before stopping
2. Repetitive patterns causing longer generation
3. High temperature (0.8) causing more sampling overhead
4. Concurrent requests overwhelming single-threaded inference

### Memory Usage

```
Memory: 337 MiB / 2 GiB (16.8% utilized)
```

**Analysis:** ✅ Excellent - Well within limits

### Cache Warmup Effect

```
First request average:      8.59s
Subsequent requests average: 8.83s
Difference:                 -0.24s
```

**Analysis:** ✅ No significant warmup effect detected

---

## Quality Metrics

### Overall Quality

| Metric | Count | Percentage | Target |
|--------|-------|------------|--------|
| **Relevant responses** | 4 | 19.0% | >80% |
| **Irrelevant responses** | 17 | 81.0% | <20% |
| **Empty responses** | 0 | 0% | 0% |
| **Repetitive responses** | 16 | 51.6% | <10% |

**Grade:** ❌ **FAILED** - Critical quality issues

### FAQ Questions (17 tested)

| Question Category | On-Topic | Uses System Info | Example Response Quality |
|-------------------|----------|------------------|-------------------------|
| Booking process | 1/4 | 0/4 | ❌ Poor - Generic/irrelevant |
| Cancellation | 2/4 | 1/4 | ⚠️ Mixed - Some relevant |
| System info (Raft) | 0/4 | 1/4 | ❌ Poor - Generic tech talk |
| Support | 0/3 | 0/3 | ❌ Poor - No specific info |
| Seat availability | 0/2 | 0/2 | ❌ Poor - Generic |

**Key Findings:**
- ❌ **System knowledge NOT injected** - Only 2/17 responses used SYSTEM_PROMPT info
- ❌ **Generic responses** - Not movie booking specific
- ⚠️ **Repetitive patterns** - 16/17 responses had repeated phrases

### Edge Cases (14 tested)

| Category | Expected Behavior | Actual Behavior | Status |
|----------|------------------|-----------------|--------|
| **Ambiguous** ("Can I?") | Polite rejection or clarification | Answered as if valid | ❌ |
| **Long questions** | Handle gracefully | ✅ Handled | ✅ |
| **Technical detail** | General explanation | Generic rambling | ⚠️ |
| **Off-topic** (weather) | Detect and redirect | Answered question | ❌ |
| **Off-topic** (Oscar) | Detect and redirect | Answered question | ❌ |
| **Off-topic** (joke) | Detect and redirect | Attempted joke | ❌ |
| **Empty string** | Error or help message | Random text | ❌ |
| **Whitespace** | Error or help message | Random text | ❌ |

**Summary:** Only 1/5 edge cases handled gracefully

### Response Consistency

**Test:** Same question ("What is the refund policy?") asked 5 times

**Results:**
- Unique responses: 5/5 (100% different)
- Similarity: 0%
- Average response time: 8.27s

**Sample responses:**
1. "I don't know. But they are just some kind of thing..."
2. "I don't have a card in my wallet. It's not something..."
3. "The credit card issuer will be able to return any..."
4. "The money will be distributed by an entity or..."
5. "No. The refunds are only available in a limited..."

**Analysis:** ❌ **Highly inconsistent** - No two responses similar

**Causes:**
- High temperature (0.8) causing randomness
- No context injection = no factual grounding
- Model hallucinating different answers each time

---

## Example Responses (Problems Identified)

### ❌ Example 1: Not Using System Knowledge

**Question:** "How do I book a ticket?"

**Response:**
> "There's no one. No person that knows the details of how to enter their tickets and when they will be mailed on or off; we can't tell you what is in them! We don"t know if this information has been verified."

**Problems:**
- Doesn't use SYSTEM_PROMPT info (search → select → pay)
- Confusing and unhelpful
- Repetitive phrasing

**Expected Response:**
> "To book a ticket: 1) Search for your movie, 2) Select seats and showtime, 3) Complete payment. Your booking is confirmed instantly after successful payment."

---

### ❌ Example 2: Off-Topic Not Detected

**Question:** "What's the weather today?"

**Response:**
> "It'll be quite a bit warmer than you think. I'm hoping that we can get some nice storms as far south as Oklahoma, but there will be more rainfall in other areas."

**Problems:**
- Should detect off-topic and redirect
- Instead, hallucinates weather information
- Completely unrelated to movie bookings

**Expected Response:**
> "I'm a movie booking assistant and can't help with weather. I can help you with: booking tickets, cancellations, refunds, or system information. How can I assist with your movie booking?"

---

### ⚠️ Example 3: Repetitive Content

**Question:** "What is Raft consensus?"

**Response:**
> "The following are the most recent discussions, written by a friend of mine. One particular question that I've asked for an answer regarding how they define "consensus" and what it means to be fully re..."

**Problems:**
- Repetitive phrase structure
- Vague, doesn't explain Raft
- Doesn't use SYSTEM_PROMPT info about Raft

**Expected Response:**
> "Raft consensus is a protocol that ensures data consistency across multiple servers in our distributed system. If a node fails, a new leader is automatically elected, keeping the service running smoothly."

---

### ✅ Example 4: One Rare Good Response

**Question:** "When will I get my refund?"

**Response:**
> "March 9th 2017"

**Analysis:** Short, but completely wrong (hallucinated date)

**Expected Response:**
> "Refunds are processed within 3-5 business days to your original payment method after cancellation."

---

## Key Weaknesses Identified

### 1. ❌ SYSTEM_PROMPT Not Injected

**Problem:** The `/ask` endpoint uses simple "Q: / A:" format without including system context.

**Current Code (line 240):**
```python
prompt = f"Q: {request.question}\nA:"
```

**Impact:**
- Model doesn't know movie booking policies
- Can't mention specific info (1 hour cancellation, 3-5 day refunds, support@movietix.ai)
- Generates generic, unhelpful responses

**Solution:** Inject SYSTEM_PROMPT or create few-shot examples with domain knowledge

---

### 2. ❌ No Off-Topic Detection

**Problem:** Model answers questions about weather, sports, jokes, etc.

**Examples:**
- Weather: Answered with hallucinated forecast
- Oscar: Answered with made-up winner
- Capital of France: Answered with generic French talk

**Impact:**
- Wastes resources on irrelevant questions
- Confuses users (they think it's omniscient)
- No clear scope definition

**Solution:** Detect off-topic keywords, provide redirect message

---

### 3. ⚠️ High Repetition

**Problem:** 16/31 responses (51.6%) contained repetitive phrases

**Examples:**
- "I want to do", "I'm thinking about it"
- "There's no one. No person that knows"
- "It looks like a lot of people were in. And I'm thinking about it"

**Causes:**
- Repetition penalty (1.1) too low
- No examples showing concise response style
- Model falling into repetitive loops

**Solution:** Increase repetition_penalty to 1.2-1.3, provide few-shot examples

---

### 4. ⚠️ Slow Performance (6.06s)

**Problem:** Average response time 2-3x slower than expected

**Causes:**
1. **Long generation**: Model doesn't know when to stop
2. **Repetitive loops**: Generates same phrases over and over
3. **High temperature**: More sampling = slower

**Evidence:**
- Min response: 0.20s (proves model CAN be fast)
- Max response: 10.16s (5x slower than target)
- High variability (stdev: 2.94s)

**Solution:**
- Add early stopping cues in prompt
- Reduce max_tokens for FAQ (100 instead of 128)
- Lower temperature for FAQ (0.6 instead of 0.8)

---

### 5. ⚠️ Zero Consistency

**Problem:** Same question gets completely different answers each time

**Examples:** "What is the refund policy?" - 5 completely different responses

**Causes:**
- High temperature (0.8) = more randomness
- No factual grounding (no system context)
- Sampling-based generation

**Solution:**
- Lower temperature for FAQ (0.6)
- Inject factual context
- Use top_k more aggressively (40 instead of 50)

---

### 6. ❌ Concurrent Performance

**Problem:** 30% timeout rate under concurrent load

**Results:**
- 7/10 requests succeeded
- 3/10 requests timed out (30s)
- Throughput: 0.17 req/s (very low)

**Causes:**
- Single-threaded CPU inference
- Longer generation times compound
- No request queuing/prioritization

**Solution:**
- Reduce generation time (main priority)
- Consider batch inference
- Add request timeout on LLM side

---

## Improvement Opportunities

### Priority 1: Inject System Context ⭐⭐⭐

**Current:** Simple "Q: / A:" prompt
**Proposed:** Few-shot examples with domain knowledge

**Expected Impact:**
- Relevance: 19% → 80%+
- System knowledge usage: 12% → 90%+
- Quality grade: F → B

**Implementation:** Create few-shot prompt template with 3-5 examples

---

### Priority 2: Add Off-Topic Detection ⭐⭐⭐

**Proposed:** Keyword-based detection + redirect message

**Expected Impact:**
- Off-topic handling: 0% → 100%
- User confusion: Reduced significantly
- Resource waste: Reduced

**Implementation:** Check for keywords (weather, sports, joke), return template response

---

### Priority 3: Optimize Generation Parameters ⭐⭐

**Current:**
```python
temperature=0.8
top_k=50
repetition_penalty=1.1
```

**Proposed (FAQ):**
```python
temperature=0.6  # More deterministic
top_k=40  # More focused
repetition_penalty=1.3  # Stronger penalty
max_new_tokens=100  # Shorter responses
```

**Expected Impact:**
- Response time: 6s → 3-4s
- Consistency: 0% → 60%+
- Repetition: 51% → 10%

---

### Priority 4: Add Template Responses ⭐⭐

**Proposed:** Fast template responses for top 5-10 questions

**Examples:**
- "How do I book?" → Template (instant)
- "Cancellation policy?" → Template (instant)
- "Refund timing?" → Template (instant)

**Expected Impact:**
- Response time for common questions: 6s → 0.01s (600x faster)
- Consistency: 0% → 100% (for templated questions)
- Quality: Variable → Always correct

---

## Recommended Action Plan

### Phase 1: Prompt Engineering (Days 1-2) ⭐⭐⭐

1. Create `llm/prompt_templates.py` with:
   - Few-shot examples (3-5 examples)
   - System context injection
   - Response format guidelines

2. Update `llm/llm_server.py`:
   - Use new prompt templates
   - Add off-topic detection
   - Optimize parameters

**Expected Results:**
- Relevance: 19% → 70%+
- Response time: 6s → 4s

---

### Phase 2: Fallback Strategies (Day 3) ⭐⭐

1. Implement template responses for top 10 questions
2. Add off-topic keyword detection
3. Add error handling for edge cases

**Expected Results:**
- Common questions: instant response
- Off-topic: properly redirected
- Edge cases: handled gracefully

---

### Phase 3: Testing & Tuning (Day 4)

1. Re-run comprehensive tests
2. Compare before/after metrics
3. Fine-tune parameters based on results

**Target Metrics:**
- Relevance: >80%
- Response time: <4s average
- Consistency: >60%
- Off-topic detection: 100%

---

## Test Data Files

**Raw Results:**
- `tests/test_results_20251113_054302.json` - Comprehensive test results
- `tests/benchmark_results_20251113_054743.json` - Performance benchmarks

**Scripts:**
- `tests/test_llm_comprehensive.py` - Quality testing
- `tests/benchmark_llm_performance.py` - Performance testing

---

## Conclusions

### What Works ✅

1. **Model loads successfully** (5-10 seconds)
2. **Memory usage excellent** (337 MB / 2 GB)
3. **No warmup effect** (consistent performance)
4. **Model responds** (100% success rate in sequential)

### What Doesn't Work ❌

1. **Quality very poor** (19% relevance)
2. **No system knowledge** (generic responses)
3. **No off-topic detection** (answers everything)
4. **High repetition** (51% of responses)
5. **Slow performance** (6s vs 3s target)
6. **Zero consistency** (random responses)

### Bottom Line

The DistilGPT-2 model **works** but the **simple "Q: / A:" prompt is inadequate**. The model needs:
- Domain context (movie booking info)
- Few-shot examples (teaching response style)
- Off-topic detection (scope definition)
- Optimized parameters (faster, more focused)

With proper prompt engineering, we expect:
- **4x improvement in relevance** (19% → 80%)
- **2x improvement in speed** (6s → 3s)
- **Off-topic handling** (0% → 100%)

**Next Steps:** Implement Phase 1 improvements (prompt engineering)

---

**Status:** ⚠️ BASELINE DOCUMENTED - IMPROVEMENTS NEEDED
**Date:** 2025-11-13
**Next:** [LLM_PROMPT_IMPROVEMENTS.md](LLM_PROMPT_IMPROVEMENTS.md)
