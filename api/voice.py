
from http.server import BaseHTTPRequestHandler
import json
import base64
import os
try:
    from api.sarvam_voice import text_to_speech, speech_to_text
except ImportError:
    try:
        from sarvam_voice import text_to_speech, speech_to_text
    except ImportError:
        import sys
        import os
        # Add current directory to path as last resort
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from sarvam_voice import text_to_speech, speech_to_text

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        origin = self.headers.get('Origin') or '*'
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Vary', 'Origin')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            action = data.get('action')
            
            if action == 'tts':
                text = data.get('text')
                if not text:
                    self.send_error(400, "Missing 'text' for TTS")
                    return
                
                lang = data.get('language', 'hi-IN')
                gender = data.get('gender', 'female')
                
                audio_base64 = text_to_speech(text, lang, gender)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "audio": audio_base64,
                    "format": "wav"  # Sarvam returns wav typically
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            elif action == 'stt':
                audio_base64 = data.get('audio')
                if not audio_base64:
                    self.send_error(400, "Missing 'audio' for STT")
                    return
                
                # Decode base64 audio
                try:
                    audio_bytes = base64.b64decode(audio_base64)
                except Exception as e:
                    self.send_error(400, f"Invalid base64 audio: {e}")
                    return

                lang = data.get('language', 'hi-IN')
                transcript = speech_to_text(audio_bytes, lang)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "text": transcript
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            else:
                self.send_error(400, f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON body")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
