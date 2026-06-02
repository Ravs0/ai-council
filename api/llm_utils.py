import os
import litellm
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# Configure LiteLLM
litellm.drop_params = True
litellm.suppress_debug_info = True

# ---------------------------------------------------------------------------
# Helper: first non-empty value from a list of env var names
# ---------------------------------------------------------------------------
def _env(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""

# ---------------------------------------------------------------------------
# Resolve native API keys so LiteLLM's auto-discovery works
# ---------------------------------------------------------------------------

# DeepSeek native — reads DEEPSEEK_API_KEY
_DEEPSEEK_NATIVE = _env("DEEPSEEK_API_KEY", "DEEPSEEK_CHAT_API_KEY", "DEEPSEEK_REASONER_API_KEY")
if _DEEPSEEK_NATIVE:
    os.environ["DEEPSEEK_API_KEY"] = _DEEPSEEK_NATIVE

# ---------------------------------------------------------------------------
# Model mapping: alias → LiteLLM model ID (strictly DeepSeek Native!)
# ---------------------------------------------------------------------------
MODEL_MAPPING = {
    # ── DeepSeek native  (platform.deepseek.com) ──────────────────────────
    "deepseek":          "deepseek/deepseek-chat",
    "deepseek-chat":     "deepseek/deepseek-chat",
    "deepseek-reasoner": "deepseek/deepseek-reasoner",
    "reasoner":          "deepseek/deepseek-reasoner",

    # ── Google (Mapped to DeepSeek Chat) ──────────────────────────────────
    "gemini-flash":      "deepseek/deepseek-chat",
    "gemini-pro":        "deepseek/deepseek-chat",
    "gemini-2-flash":    "deepseek/deepseek-chat",

    # ── Groq (Mapped to DeepSeek Chat) ────────────────────────────────────
    "groq":              "deepseek/deepseek-chat",
    "llama":             "deepseek/deepseek-chat",

    # ── NVIDIA NIM custom endpoints (Mapped to DeepSeek Chat) ─────────────
    "deepseek-nvidia":   "deepseek/deepseek-chat",
    "kimi":              "deepseek/deepseek-chat",
    "minimax":           "deepseek/deepseek-chat",

    # ── Sarvam (Mapped to DeepSeek Chat) ──────────────────────────────────
    "sarvam":            "deepseek/deepseek-chat",
}

# ---------------------------------------------------------------------------
# Custom endpoints (Cleared out to adhere to DeepSeek exclusivity)
# ---------------------------------------------------------------------------
CUSTOM_ENDPOINTS = {}

MAX_PROMPT_CHARS = 16_000
MIN_TOKENS = 64
MAX_TOKENS = 4_000

# Exports for compatibility
MODEL_ALIASES = MODEL_MAPPING
RateLimitError = litellm.RateLimitError


class LLMClient:
    def __init__(self):
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(
            (litellm.RateLimitError, litellm.APIConnectionError, litellm.Timeout)
        ),
    )
    def call_model(
        self,
        model_alias: str,
        prompt: str,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 1000,
    ) -> str:
        model_alias = (model_alias or "").strip().lower()
        model_id = MODEL_MAPPING.get(model_alias, "deepseek/deepseek-chat")

        try:
            response = completion(
                model=model_id,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.55,
                timeout=25,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logging.error(f"LiteLLM error '{model_alias}' ({model_id}): {e}")
            raise

