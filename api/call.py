from http.server import BaseHTTPRequestHandler
import json
import os
from api.llm_utils import LLMClient, RateLimitError, MODEL_ALIASES, MAX_PROMPT_CHARS, MIN_TOKENS, MAX_TOKENS


def _safe_int(v, fallback):
    try:
        return int(v)
    except (TypeError, ValueError):
        return fallback


def _cors_headers(handler, origin: str):
    """Write CORS headers. Always allow the request's origin (we validate at app level)."""
    handler.send_header("Access-Control-Allow-Origin", origin or "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Vary", "Origin")


class handler(BaseHTTPRequestHandler):

    def _origin(self) -> str:
        """Return the request origin, or '*' if none."""
        return self.headers.get("Origin") or "*"

    def do_OPTIONS(self):
        """Respond to CORS preflight — always allow so the browser can POST."""
        self.send_response(200)
        _cors_headers(self, self._origin())
        self.end_headers()

    def do_POST(self):
        origin = self._origin()

        try:
            length = _safe_int(self.headers.get("Content-Length", 0), 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw)
        except json.JSONDecodeError:
            return self._json(400, {"error": "Invalid JSON body."}, origin)

        model_key = (body.get("model") or "").strip().lower()
        prompt    = (body.get("prompt") or "").strip()

        if not prompt:
            return self._json(400, {"error": "Prompt is required."}, origin)
        if len(prompt) > MAX_PROMPT_CHARS:
            return self._json(400, {"error": f"Prompt too long (>{MAX_PROMPT_CHARS} chars)."}, origin)

        system     = (body.get("system") or "You are a helpful assistant.").strip()
        max_tokens = _safe_int(body.get("max_tokens", 700), 700)
        max_tokens = max(MIN_TOKENS, min(MAX_TOKENS, max_tokens))

        # Synthesis / research-agent is too slow for a single Vercel function.
        # Guard it upfront with a clear explanation rather than a silent timeout.
        if model_key == "research-agent":
            return self._json(503, {
                "error": (
                    "The 7-Phase Synthesis Protocol requires a long-running worker "
                    "and cannot run inside a Vercel serverless function (60 s limit). "
                    "Run the local server for Synthesis mode."
                )
            }, origin)

        client = LLMClient()

        try:
            text = client.call_model(model_key, prompt, system, max_tokens)
            return self._json(200, {"text": text}, origin)

        except ValueError as ve:
            return self._json(400, {"error": str(ve)}, origin)
        except RateLimitError:
            return self._json(429, {"error": "Rate limit hit. Please wait a moment and retry."}, origin)
        except Exception as e:
            return self._json(502, {"error": f"Model error: {str(e)}"}, origin)

    def _json(self, code: int, data: dict, origin: str):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self, origin)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
