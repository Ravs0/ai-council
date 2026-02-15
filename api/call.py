from http.server import BaseHTTPRequestHandler
import json
import os
import re
import requests as http

MODELS = {
    "deepseek": {
        "name": "DeepSeek V3.2",
        "model_id": "deepseek-ai/deepseek-v3.2",
        "api_key": os.environ.get("DEEPSEEK_NVIDIA_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1"
    },
    "kimi": {
        "name": "Kimi K2.5",
        "model_id": "moonshotai/kimi-k2.5",
        "api_key": os.environ.get("KIMI_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1"
    },
    "minimax": {
        "name": "Minimax M2.1",
        "model_id": "minimaxai/minimax-m2.1",
        "api_key": os.environ.get("MINIMAX_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1"
    },
    "reasoner": {
        "name": "DeepSeek Reasoner",
        "model_id": "deepseek-reasoner",
        "api_key": os.environ.get("DEEPSEEK_REASONER_API_KEY"),
        "base_url": "https://api.deepseek.com/v1"
    },
}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        mk = body.get('model')
        prompt = body.get('prompt', '')
        system = body.get('system', 'You are a helpful assistant.')
        max_tokens = body.get('max_tokens', 1000)

        # ─── GEMINI HANDLER ──────────────────────────────────────────────────
        if mk and mk.startswith("gemini"):
            # Hardcoded key as per user instruction
            api_key = "[REDACTED]"
            
            # Map simplified names to real model IDs
            # Per user scan list: models/gemini-3-flash-preview, models/gemini-3-pro-preview
            # Switching 'flash' to 2.0 for stability/speed per user report of timeouts
            real_model = "gemini-2.0-flash" 
            if "flash" in mk: real_model = "gemini-2.0-flash"
            elif "pro" in mk: real_model = "gemini-2.0-pro-exp-02-05" # Trying 2.0 Pro Experimental (smartest) or fallback to 1.5 Pro

            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model}:generateContent?key={api_key}"
            
            g_payload = {
                "contents": [{
                    "parts": [{"text": f"{system}\n\n{prompt}"}] 
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": max_tokens
                }
            }
            
            try:
                resp = http.post(url, json=g_payload, headers={'Content-Type': 'application/json'}, timeout=55)
                
                # Fallback logic if 'gemini-3-flash-preview' fails (sometimes preview names change)
                if resp.status_code == 404 or resp.status_code == 400:
                    fallback = "gemini-2.0-flash"
                    print(f"Gemini 3 model {real_model} error {resp.status_code}, strictly falling back to {fallback}")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{fallback}:generateContent?key={api_key}"
                    resp = http.post(url, json=g_payload, headers={'Content-Type': 'application/json'}, timeout=55)

                resp.raise_for_status()
                result = resp.json()
                # Safe extraction of text
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                if not text:
                    text = "[Gemini Error: No text returned. Check API quotas.]"
                
                return self._json(200, {"text": text})

            except Exception as e:
                return self._json(500, {"error": f"Gemini Error: {str(e)}"})

        # ─── EXISTING HANDLER (DeepSeek/Minimax) ─────────────────────────────
        config = MODELS.get(body.get('model'))
        if not config or not config.get('api_key'):
            return self._json(400, {"error": f"Model {mk} not configured"})

        url = f"{config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": config["model_id"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.6
        }

        try:
            resp = http.post(url, headers=headers, json=payload, timeout=55)
            resp.raise_for_status()
            data = resp.json()
            msg = data.get("choices", [{}])[0].get("message", {})
            text = msg.get("content") or msg.get("reasoning_content") or ""
            text = re.sub(r'<(think|thought)>[\s\S]*?</\1>\s*', '', text, flags=re.IGNORECASE).strip()
            return self._json(200, {"text": text})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
