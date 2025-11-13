"""
Prompt Templates and Fallback Strategies for DistilGPT-2 Movie Booking Assistant
Provides context injection, few-shot examples, and template responses
"""

# ===========================================
# SYSTEM CONTEXT (Movie Booking Domain)
# ===========================================

SYSTEM_CONTEXT = """Movie Ticket Booking System

Key Information:
- Booking: Search movies → Select seats & showtime → Pay → Instant confirmation
- Cancellation: Allowed up to 1 hour before showtime
- Refunds: Processed within 3-5 business days to original payment method
- System: Uses Raft consensus protocol for fault tolerance and data consistency
- Failed Payment: Seats NOT reserved - retry freely
- Node Failures: Automatic leader election ensures continuous service
- Support: support@movietix.ai"""

# ===========================================
# FEW-SHOT EXAMPLES (Teaching Response Style)
# ===========================================

FEW_SHOT_EXAMPLES = """Q: How do I book a ticket?
A: To book: 1) Search for your movie, 2) Select seats and showtime, 3) Complete payment. Your booking is confirmed instantly after successful payment.

Q: What is the cancellation policy?
A: You can cancel bookings up to 1 hour before showtime. Refunds are processed within 3-5 business days to your original payment method.

Q: What happens if a node fails?
A: The system uses Raft consensus protocol. If a node fails, a new leader is automatically elected to ensure continuous service and data consistency.

Q: How do I contact support?
A: For assistance, email support@movietix.ai. The system automatically handles most technical issues using Raft consensus.

Q: When do I get my refund?
A: Refunds are processed within 3-5 business days after cancellation to your original payment method."""

# ===========================================
# PROMPT TEMPLATES
# ===========================================

def get_fewshot_prompt(question: str) -> str:
    """
    Few-shot prompt with domain context and examples
    Best for: General questions
    """
    return f"""{SYSTEM_CONTEXT}

Example Questions & Answers:
{FEW_SHOT_EXAMPLES}

Q: {question}
A:"""


def get_hybrid_prompt(question: str) -> str:
    """
    Hybrid approach: Context + fewer examples
    Best for: Balance of speed and quality
    """
    return f"""{SYSTEM_CONTEXT}

Examples:
Q: How do I book?
A: Search movie → Select seats → Pay → Instant confirmation

Q: Cancellation policy?
A: Cancel up to 1 hour before showtime. Refunds in 3-5 business days.

Q: {question}
A:"""


def get_simple_context_prompt(question: str) -> str:
    """
    Simple context injection without examples
    Best for: Speed when examples not needed
    """
    return f"""{SYSTEM_CONTEXT}

Q: {question}
A:"""


# ===========================================
# TEMPLATE RESPONSES (Fast, Consistent)
# ===========================================

TEMPLATE_RESPONSES = {
    # Booking
    "how_to_book": "To book a ticket: 1) Search for your movie, 2) Select seats and showtime, 3) Complete payment. Your booking is confirmed instantly after successful payment.",

    "payment_methods": "The system accepts all major credit cards and digital payment methods. Payment is processed securely at checkout.",

    "seat_selection": "Yes, you can select specific seats during booking. Available seats are shown in real-time on the seating chart.",

    "booking_confirmation": "You'll receive instant confirmation after successful payment. Check your email or account for booking details.",

    # Cancellation & Refunds
    "cancel_booking": "You can cancel bookings up to 1 hour before showtime via the application. Navigate to 'My Bookings' and select cancel.",

    "cancellation_policy": "Cancellations are allowed up to 1 hour before showtime. After that, bookings cannot be cancelled.",

    "refund_timing": "Refunds are processed within 3-5 business days to your original payment method after cancellation.",

    "refund_policy": "Refunds are issued for cancellations made at least 1 hour before showtime. Processing takes 3-5 business days.",

    # System Information
    "raft_consensus": "Raft consensus is a protocol that ensures data consistency across multiple servers. It automatically elects a leader and handles failures to keep the service running.",

    "fault_tolerance": "The system uses Raft consensus with multiple nodes. If one node fails, a new leader is automatically elected, ensuring continuous service.",

    "node_failure": "When a node crashes, the Raft protocol automatically elects a new leader from the remaining nodes, maintaining service availability.",

    "data_consistency": "Data consistency is maintained through Raft consensus, which ensures all nodes agree on the current state before confirming operations.",

    # Seat Availability
    "check_availability": "Seat availability is shown in real-time on the movie details page. Select your desired showtime to view available seats.",

    "full_seats": "If a showing is full, try another showtime or check back later for cancellations that might free up seats.",

    "multiple_tickets": "Yes, you can book multiple tickets in a single transaction. Select the number of tickets during checkout.",

    # Support
    "contact_support": "For assistance, contact support@movietix.ai. The system automatically handles most technical issues.",

    "support_email": "You can reach support at support@movietix.ai for any questions or issues.",

    # Payment Issues
    "payment_failed": "If payment fails, your seats are NOT reserved. You can retry the payment freely without losing the seats.",

    # General Help
    "help": "I can help you with: booking tickets, checking seat availability, cancellation policies, refunds, and system information. What would you like to know?",
}


# ===========================================
# OFF-TOPIC DETECTION
# ===========================================

OFF_TOPIC_KEYWORDS = [
    # Weather
    "weather", "temperature", "rain", "snow", "forecast", "sunny", "cloudy",

    # Sports
    "score", "game", "team", "player", "match", "championship", "football", "basketball",

    # Entertainment (non-movie)
    "song", "music", "album", "concert", "festival",

    # News/Current Events
    "news", "election", "president", "politics", "war",

    # General Knowledge
    "capital", "country", "president", "who invented", "when was", "history",

    # Personal Requests
    "joke", "story", "recipe", "how to cook", "exercise",

    # Technology (non-system)
    "program in", "code in", "algorithm for", "tutorial", "how to install",

    # Stock/Finance
    "stock", "crypto", "bitcoin", "investment", "market",
]

OFF_TOPIC_RESPONSE = """I'm a movie ticket booking assistant and can only help with:
- Booking movie tickets
- Cancellation and refunds
- Seat availability
- System information (Raft consensus)
- Support contact

How can I assist you with your movie booking?"""


def is_off_topic(question: str) -> bool:
    """Check if question is off-topic"""
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in OFF_TOPIC_KEYWORDS)


# ===========================================
# KEYWORD MATCHING FOR TEMPLATE RESPONSES
# ===========================================

TEMPLATE_KEYWORDS = {
    # Booking
    "how_to_book": ["how to book", "how do i book", "booking process", "book a ticket"],
    "payment_methods": ["payment method", "how to pay", "payment option", "accepted payment"],
    "seat_selection": ["select seat", "choose seat", "pick seat", "specific seat"],
    "booking_confirmation": ["booking confirm", "confirmation", "how do i know", "is my booking"],

    # Cancellation
    "cancel_booking": ["how to cancel", "cancel my booking", "cancel ticket"],
    "cancellation_policy": ["cancellation policy", "cancel policy", "cancellation rule"],
    "refund_timing": ["when will i get refund", "refund time", "how long refund"],
    "refund_policy": ["refund policy", "refund rule", "get refund"],

    # System
    "raft_consensus": ["what is raft", "raft consensus", "explain raft"],
    "fault_tolerance": ["handle failure", "fault tolerance", "system fail"],
    "node_failure": ["node crash", "node fail", "what if node"],
    "data_consistency": ["data consistency", "consistent", "consistency maintained"],

    # Availability
    "check_availability": ["check availability", "check seat", "available seat"],
    "full_seats": ["seats full", "sold out", "no seat"],
    "multiple_tickets": ["multiple ticket", "book multiple", "several ticket"],

    # Support
    "contact_support": ["contact support", "reach support", "support email"],
    "support_email": ["support email", "support contact", "help email"],

    # Payment
    "payment_failed": ["payment failed", "payment error", "payment not work"],

    # Help
    "help": ["help", "what can you do", "assist", "support"],
}


def find_template_response(question: str) -> str:
    """
    Find matching template response based on keywords
    Returns template response or None
    """
    question_lower = question.lower()

    for template_key, keywords in TEMPLATE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return TEMPLATE_RESPONSES.get(template_key)

    return None


# ===========================================
# GENERATION PARAMETERS
# ===========================================

FAQ_GENERATION_PARAMS = {
    "max_new_tokens": 100,  # Shorter for concise answers
    "temperature": 0.6,  # More deterministic than 0.8
    "top_p": 0.92,  # Slightly more focused
    "top_k": 40,  # More focused vocabulary
    "repetition_penalty": 1.3,  # Stronger than 1.1
    "do_sample": True,
    "early_stopping": True,
}

CHAT_GENERATION_PARAMS = {
    "max_new_tokens": 150,  # Longer for conversation
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "do_sample": True,
    "early_stopping": True,
}


# ===========================================
# RESPONSE POST-PROCESSING
# ===========================================

def clean_response(answer: str) -> str:
    """
    Clean up LLM response
    - Remove trailing Q: patterns
    - Remove excessive whitespace
    - Trim to reasonable length
    """
    # Remove trailing Q: if model repeats pattern
    if "\nQ:" in answer:
        answer = answer.split("\nQ:")[0]

    # Remove trailing A: if present
    if "\nA:" in answer:
        answer = answer.split("\nA:")[0]

    # Strip whitespace
    answer = answer.strip()

    # Remove multiple newlines
    import re
    answer = re.sub(r'\n{3,}', '\n\n', answer)

    # Trim if too long (over 500 chars)
    if len(answer) > 500:
        # Find last sentence within 500 chars
        truncated = answer[:500]
        last_period = truncated.rfind('.')
        if last_period > 200:  # At least 200 chars
            answer = answer[:last_period + 1]

    return answer


def validate_response(answer: str, question: str) -> str:
    """
    Validate response and provide fallback if needed
    Returns: cleaned answer or fallback message
    """
    # Clean first
    answer = clean_response(answer)

    # Check if empty
    if not answer or len(answer) < 10:
        return "I apologize, but I couldn't generate a proper response. Could you rephrase your question about movie bookings?"

    # Check for repetitive patterns (same word 5+ times in a row)
    words = answer.lower().split()
    for i in range(len(words) - 4):
        if len(set(words[i:i+5])) == 1:  # All 5 words are the same
            return "I apologize, but I couldn't generate a proper response. Could you rephrase your question about movie bookings?"

    return answer


# ===========================================
# MAIN RESPONSE GENERATOR
# ===========================================

def generate_response(question: str, use_llm_func, generation_params: dict) -> str:
    """
    Main response generation logic with fallback strategy

    Priority:
    1. Off-topic detection
    2. Template response (if keyword match)
    3. LLM generation with improved prompt
    4. Fallback for errors

    Args:
        question: User's question
        use_llm_func: Function to call LLM (passes prompt)
        generation_params: Generation parameters dict

    Returns:
        Final answer string
    """
    # Step 1: Check for off-topic
    if is_off_topic(question):
        return OFF_TOPIC_RESPONSE

    # Step 2: Check for template response (instant, consistent)
    template_response = find_template_response(question)
    if template_response:
        return template_response

    # Step 3: Use LLM with improved prompt
    try:
        # Use few-shot prompt for best quality
        prompt = get_fewshot_prompt(question)

        # Call LLM
        raw_answer = use_llm_func(prompt, generation_params)

        # Validate and clean
        final_answer = validate_response(raw_answer, question)

        return final_answer

    except Exception as e:
        # Step 4: Fallback for errors
        return f"I apologize, but I encountered an error processing your question. Please try rephrasing or contact support@movietix.ai. (Error: {str(e)[:50]})"


# ===========================================
# USAGE EXAMPLE
# ===========================================

if __name__ == "__main__":
    # Example: Test template matching
    test_questions = [
        "How do I book a ticket?",
        "What's the weather?",
        "When do I get my refund?",
        "Tell me about Raft consensus",
        "Random question",
    ]

    print("Template Response Test:")
    print("=" * 60)
    for q in test_questions:
        print(f"\nQ: {q}")

        if is_off_topic(q):
            print(f"A: [OFF-TOPIC] {OFF_TOPIC_RESPONSE[:100]}...")
        else:
            template = find_template_response(q)
            if template:
                print(f"A: [TEMPLATE] {template}")
            else:
                print(f"A: [LLM NEEDED]")

    print("\n" + "=" * 60)
    print("\nPrompt Templates Test:")
    print("=" * 60)

    test_q = "How does the system handle failures?"
    print(f"\nFew-Shot Prompt for: '{test_q}'")
    print("-" * 60)
    print(get_fewshot_prompt(test_q))
