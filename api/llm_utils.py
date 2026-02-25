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

# Gemini — reads GEMINI_API_KEY
_GEMINI = _env("GEMINI_API_KEY", "GOOGLE_API_KEY")
if _GEMINI:
    os.environ["GEMINI_API_KEY"] = _GEMINI

# Groq — reads GROQ_API_KEY
_GROQ = _env("GROQ_API_KEY")
if _GROQ:
    os.environ["GROQ_API_KEY"] = _GROQ

# Sarvam — not a LiteLLM native, handled explicitly
_SARVAM = _env("SARVAM_API_KEY")

# NVIDIA NIM key (shared across Kimi, Minimax, DeepSeek-NVIDIA)
_NVIDIA = _env("DEEPSEEK_NVIDIA_API_KEY", "NVIDIA_API_KEY")

# ---------------------------------------------------------------------------
# Model mapping: alias → LiteLLM model ID
# ---------------------------------------------------------------------------
MODEL_MAPPING = {
    # ── DeepSeek native  (platform.deepseek.com) ──────────────────────────
    "deepseek":          "deepseek/deepseek-chat",
    "deepseek-chat":     "deepseek/deepseek-chat",
    "deepseek-reasoner": "deepseek/deepseek-reasoner",
    "reasoner":          "deepseek/deepseek-reasoner",

    # ── Google ────────────────────────────────────────────────────────────
    "gemini-flash":      "gemini/gemini-1.5-flash",
    "gemini-pro":        "gemini/gemini-1.5-pro",
    "gemini-2-flash":    "gemini/gemini-2.0-flash",

    # ── Groq ──────────────────────────────────────────────────────────────
    "groq":              "groq/llama-3.3-70b-versatile",
    "llama":             "groq/llama-3.3-70b-versatile",

    # ── NVIDIA NIM custom endpoints ───────────────────────────────────────
    # Use these aliases explicitly when you want the NVIDIA route
    "deepseek-nvidia":   "openai/nvidia/deepseek-ai/deepseek-r1",
    "kimi":              "openai/moonshotai/kimi-k2.5",
    "minimax":           "openai/minimaxai/minimax-m2.1",

    # ── Sarvam ────────────────────────────────────────────────────────────
    "sarvam":            "openai/sarvam-m",
}

# ---------------------------------------------------------------------------
# Custom endpoints: only used when the alias is in this dict AND the key exists
# ---------------------------------------------------------------------------
CUSTOM_ENDPOINTS = {
    "deepseek-nvidia": {
        "api_key":  _NVIDIA,
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "kimi": {
        "api_key":  _env("KIMI_API_KEY") or _NVIDIA,
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "minimax": {
        "api_key":  _env("MINIMAX_API_KEY") or _NVIDIA,
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "sarvam": {
        "api_key":  _SARVAM,
        "base_url": "https://api.sarvam.ai/v1",
    },
}

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
        model_id = MODEL_MAPPING.get(model_alias, model_alias)

        api_base = None
        api_key = None

        # Only apply custom endpoint when the key actually exists
        if model_alias in CUSTOM_ENDPOINTS:
            config = CUSTOM_ENDPOINTS[model_alias]
            ep_key = (config.get("api_key") or "").strip()
            if ep_key:
                api_base = config["base_url"]
                api_key  = ep_key
                if not model_id.startswith("openai/"):
                    model_id = f"openai/{model_id}"
            else:
                logging.warning(
                    f"No API key for custom endpoint '{model_alias}'. "
                    "Routing through LiteLLM natively."
                )

        try:
            response = completion(
                model=model_id,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.55,
                api_base=api_base,
                api_key=api_key,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logging.error(f"LiteLLM error '{model_alias}' ({model_id}): {e}")
            raise
