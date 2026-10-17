"""Token usage and cost estimation helper."""

# Pricing per million tokens (USD) - Approximate current rates
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    "mock": {"prompt": 0.0, "completion": 0.0},
}


def estimate_tokens(text: str) -> int:
    """Fast, lightweight token count estimation (~4 characters per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "mock") -> float:
    """Calculate estimated cost in USD."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["mock"])
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
    return round(prompt_cost + completion_cost, 6)
