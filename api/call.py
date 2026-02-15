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

        config = MODELS.get(mk)
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
