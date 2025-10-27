"""
Configuration management for the SQL agent evaluation framework.
Supports multiple LLM providers: Gemini, Claude, OpenAI, and Ollama.
"""

import os
from typing import Optional, Literal
from dotenv import load_dotenv

load_dotenv()

ModelProvider = Literal["gemini", "claude", "openai", "ollama"]


class EvaluationConfig:
    """Central configuration for evaluation framework."""

    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Model Configuration
    EVAL_MODEL: str = os.getenv("EVAL_MODEL", "gemini-1.5-flash")

    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    # DeepEval Settings
    DEEPEVAL_THRESHOLD: float = float(os.getenv("DEEPEVAL_THRESHOLD", "0.7"))
    DEEPEVAL_VERBOSE: bool = os.getenv("DEEPEVAL_VERBOSE", "true").lower() == "true"

    # Agentcore
    AGENTCORE_API_KEY: Optional[str] = os.getenv("AGENTCORE_API_KEY")
    AGENTCORE_PROJECT_ID: str = os.getenv("AGENTCORE_PROJECT_ID", "sql-agent-eval")

    # Strands
    STRANDS_LOG_LEVEL: str = os.getenv("STRANDS_LOG_LEVEL", "INFO")

    @classmethod
    def get_model_provider(cls) -> ModelProvider:
        """Determine which model provider to use based on EVAL_MODEL."""
        model = cls.EVAL_MODEL.lower()

        if model.startswith("gemini"):
            return "gemini"
        elif model.startswith("claude"):
            return "claude"
        elif model.startswith("gpt"):
            return "openai"
        elif model.startswith("ollama/"):
            return "ollama"
        else:
            # Default to gemini if unclear
            return "gemini"

    @classmethod
    def get_model_config(cls) -> dict:
        """
        Get model configuration for DeepEval metrics.
        Returns a dict that can be passed to DeepEval metric constructors.
        """
        provider = cls.get_model_provider()

        if provider == "gemini":
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set in environment")
            return {
                "model": cls.EVAL_MODEL,
                "provider": "google"
            }

        elif provider == "claude":
            if not cls.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            return {
                "model": cls.EVAL_MODEL,
                "provider": "anthropic"
            }

        elif provider == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            return {
                "model": cls.EVAL_MODEL,
                "provider": "openai"
            }

        elif provider == "ollama":
            # Extract model name after "ollama/"
            model_name = cls.EVAL_MODEL.split("/", 1)[1] if "/" in cls.EVAL_MODEL else cls.OLLAMA_MODEL
            return {
                "model": model_name,
                "provider": "ollama",
                "base_url": cls.OLLAMA_BASE_URL
            }

        raise ValueError(f"Unknown model provider for: {cls.EVAL_MODEL}")

    @classmethod
    def validate_config(cls) -> None:
        """Validate that required configuration is present."""
        provider = cls.get_model_provider()

        if provider == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required when using Gemini models. "
                "Set it in your .env file or environment variables."
            )
        elif provider == "claude" and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Claude models. "
                "Set it in your .env file or environment variables."
            )
        elif provider == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI models. "
                "Set it in your .env file or environment variables."
            )

        print(f"✓ Using model: {cls.EVAL_MODEL} (provider: {provider})")


# Model comparison helper
MODEL_RECOMMENDATIONS = {
    "cost_effective": {
        "model": "gemini-1.5-flash",
        "pros": ["Very cheap (~$0.075/1M tokens)", "Fast", "Good for CI/CD"],
        "cons": ["Slightly less accurate than premium models"]
    },
    "best_accuracy": {
        "model": "claude-3-5-sonnet-20241022",
        "pros": ["Superior reasoning", "Best for complex SQL", "Excellent context understanding"],
        "cons": ["More expensive", "Slower than Flash models"]
    },
    "balanced": {
        "model": "gemini-1.5-pro",
        "pros": ["Good accuracy", "Reasonable cost", "Large context window"],
        "cons": ["Slower than Flash"]
    },
    "free_local": {
        "model": "ollama/qwen2.5-coder:7b",
        "pros": ["Completely free", "No API limits", "Privacy"],
        "cons": ["Requires local GPU", "Slower", "Less accurate"]
    }
}


def print_model_recommendations():
    """Print available model options and recommendations."""
    print("\n🤖 Available Model Options:\n")
    for category, info in MODEL_RECOMMENDATIONS.items():
        print(f"  {category.replace('_', ' ').title()}:")
        print(f"    Model: {info['model']}")
        print(f"    Pros: {', '.join(info['pros'])}")
        print(f"    Cons: {', '.join(info['cons'])}")
        print()


if __name__ == "__main__":
    # Test configuration
    print_model_recommendations()
    print("\nCurrent Configuration:")
    print(f"  EVAL_MODEL: {EvaluationConfig.EVAL_MODEL}")
    print(f"  Provider: {EvaluationConfig.get_model_provider()}")
    try:
        EvaluationConfig.validate_config()
        print(f"  Model Config: {EvaluationConfig.get_model_config()}")
    except ValueError as e:
        print(f"  ❌ Configuration Error: {e}")
