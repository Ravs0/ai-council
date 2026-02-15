from http.server import BaseHTTPRequestHandler
import json
import os
import re
import time

import requests as http

MODELS = {
    "deepseek": {
        "name": "DeepSeek V3.2",
        "model_id": "deepseek-ai/deepseek-v3.2",
        "api_key": os.environ.get("DEEPSEEK_NVIDIA_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "kimi": {
        "name": "Kimi K2.5",
        "model_id": "moonshotai/kimi-k2.5",
        "api_key": os.environ.get("KIMI_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "minimax": {
        "name": "Minimax M2.1",
        "model_id": "minimaxai/minimax-m2.1",
        "api_key": os.environ.get("MINIMAX_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    "reasoner": {
        "name": "DeepSeek Reasoner",
        "model_id": "deepseek-reasoner",
        "api_key": os.environ.get("DEEPSEEK_REASONER_API_KEY"),
        "base_url": "https://api.deepseek.com/v1",
    },
}

MODEL_ALIASES = {
    "deepseek_reasoner": "reasoner",
    "deepseek-reasoner": "reasoner",
    "gemini_flash": "gemini-flash",
    "gemini_pro": "gemini-pro",
}

MAX_PROMPT_CHARS = 16000
MIN_TOKENS = 64
MAX_TOKENS = 1200
MAX_RETRIES = 2
REQUEST_TIMEOUT = (4, 16)


def _safe_int(v, fallback):
    try:
        return int(v)
    except (TypeError, ValueError):
        return fallback


def _extract_text(data):
    message = data.get("choices", [{}])[0].get("message", {})
    text = message.get("content") or message.get("reasoning_content") or ""
    return re.sub(r"<(think|thought)>[\s\S]*?</\1>\s*", "", text, flags=re.IGNORECASE).strip()


def _extract_gemini_text(data):
    candidates = data.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    text_chunks = [p.get("text", "") for p in parts if isinstance(p, dict)]
    return "\n".join(chunk for chunk in text_chunks if chunk).strip()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = _safe_int(self.headers.get("Content-Length", 0), 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw)
        except json.JSONDecodeError:
            return self._json(400, {"error": "Invalid JSON body."})

        model_key = (body.get("model") or "").strip().lower()
        model_key = MODEL_ALIASES.get(model_key, model_key)
        prompt = (body.get("prompt") or "").strip()
        if not prompt:
            return self._json(400, {"error": "Prompt is required."})
        if len(prompt) > MAX_PROMPT_CHARS:
            return self._json(400, {"error": f"Prompt too long (>{MAX_PROMPT_CHARS} chars)."})

        system = (body.get("system") or "You are a helpful assistant.").strip()
        max_tokens = _safe_int(body.get("max_tokens", 700), 700)
        max_tokens = max(MIN_TOKENS, min(MAX_TOKENS, max_tokens))

        if model_key in ("gemini-flash", "gemini-pro"):
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return self._json(400, {"error": "Model gemini is not configured."})

            gemini_model = "gemini-3-flash" if model_key == "gemini-flash" else "gemini-2.5-pro"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                "generationConfig": {
                    "temperature": 0.55,
                    "maxOutputTokens": max_tokens,
                },
            }

            last_error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = http.post(url, json=payload, timeout=REQUEST_TIMEOUT)
                    if response.status_code in (404,) and model_key == "gemini-flash":
                        gemini_model = "gemini-2.5-flash"
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
                        response = http.post(url, json=payload, timeout=REQUEST_TIMEOUT)

                    if response.status_code in (408, 409, 429, 500, 502, 503, 504):
                        last_error = f"upstream {response.status_code}"
                        if attempt < MAX_RETRIES:
                            time.sleep(0.6 * (attempt + 1))
                            continue
                    response.raise_for_status()
                    data = response.json()
                    text = _extract_gemini_text(data)
                    return self._json(200, {"text": text})
                except (http.exceptions.Timeout, http.exceptions.ConnectionError):
                    last_error = "provider timeout"
                    if attempt < MAX_RETRIES:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                except (http.exceptions.HTTPError, ValueError):
                    last_error = "upstream response error"
                    if attempt < MAX_RETRIES:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    break
                except Exception:
                    last_error = "internal request error"
                    break

            return self._json(502, {"error": f"Model request failed ({last_error})."})

        config = MODELS.get(model_key)
        if not config:
            return self._json(400, {"error": "Unsupported model."})
        if not config.get("api_key"):
            return self._json(400, {"error": f"Model {model_key} is not configured."})

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config["model_id"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.55,
        }

        url = f"{config['base_url']}/chat/completions"
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = http.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)

                if response.status_code in (408, 409, 429, 500, 502, 503, 504):
                    last_error = f"upstream {response.status_code}"
                    if attempt < MAX_RETRIES:
                        time.sleep(0.6 * (attempt + 1))
                        continue

                response.raise_for_status()
                data = response.json()
                text = _extract_text(data)
                return self._json(200, {"text": text})
            except (http.exceptions.Timeout, http.exceptions.ConnectionError):
                last_error = "provider timeout"
                if attempt < MAX_RETRIES:
                    time.sleep(0.5 * (attempt + 1))
                    continue
            except (http.exceptions.HTTPError, ValueError):
                last_error = "upstream response error"
                if attempt < MAX_RETRIES:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
            except Exception:
                last_error = "internal request error"
                break

        return self._json(502, {"error": f"Model request failed ({last_error})."})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
