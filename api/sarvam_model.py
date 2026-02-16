
import os
import requests
import time

MAX_RETRIES = 2
REQUEST_TIMEOUT = (4, 16)
SARVAM_BASE_URL = "https://api.sarvam.ai/v1"

def call_sarvam(model_id, prompt, system_prompt, max_tokens=700):
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Sarvam might behave better with a standard message structure
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }

    url = f"{SARVAM_BASE_URL}/chat/completions"
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code in (429, 500, 502, 503, 504):
                last_error = f"upstream {response.status_code}"
                if attempt < MAX_RETRIES:
                    time.sleep(1 * (attempt + 1))
                    continue
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content carefully
            choices = data.get("choices", [])
            if not choices:
                return ""
                
            return choices[0].get("message", {}).get("content", "")

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            last_error = "provider timeout"
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
        except Exception as e:
            last_error = f"error: {str(e)}"
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            break

    raise RuntimeError(f"Sarvam request failed: {last_error}")
