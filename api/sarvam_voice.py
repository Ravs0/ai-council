
import os
import requests
import base64
import json

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

def text_to_speech(text, language_code="hi-IN", speaker_gender="female", sample_rate=16000):
    """
    Generate speech from text using Sarvam AI.
    Returns: base64 encoded audio string
    """
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY not configured")

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker_gender": speaker_gender,
        "speech_sample_rate": sample_rate,
        "enable_preprocessing": True,
        "model": "bulbul:v1"
    }

    try:
        response = requests.post(SARVAM_TTS_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Audio is returned as base64 string in 'audios' list
        data = response.json()
        if "audios" in data and len(data["audios"]) > 0:
            return data["audios"][0]
        else:
            raise RuntimeError("No audio returned from Sarvam API")
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Sarvam TTS request failed: {str(e)}")

def speech_to_text(audio_file_content, language_code="hi-IN", with_diarization=False):
    """
    Transcribe speech to text using Sarvam AI.
    audio_file_content: bytes or file-like object of the audio file (wav/mp3)
    Returns: transcribed text
    """
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY not configured")

    headers = {
        "api-subscription-key": api_key
    }
    
    files = {
        'file': ('audio.wav', audio_file_content, 'audio/wav')
    }
    
    data = {
        'language_code': language_code,
        'model': 'saarika:v1',
        'with_diarization': str(with_diarization).lower()
    }

    try:
        response = requests.post(SARVAM_STT_URL, headers=headers, files=files, data=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get("transcript", "")
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Sarvam STT request failed: {str(e)}")
