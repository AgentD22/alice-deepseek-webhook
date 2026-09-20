import os
import json
import httpx
from http.server import BaseHTTPRequestHandler

# Получаем настройки из переменных окружения
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
SYSTEM_PROMPT = os.environ.get('SYSTEM_PROMPT', 'Ты полезный ассистент Агент GPT. Отвечай кратко (3-5 предложений обычно и не более 10 предложений если много информации, если не попросят другое) и по делу на русском языке.')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Тексты ответов
TEXT_NOT_UNDERSTOOD = os.environ.get('TEXT_NOT_UNDERSTOOD', 'Я что-то не понял, что ты сказал. Повторите.')
TEXT_DEEPSEEK_ERROR = os.environ.get('TEXT_DEEPSEEK_ERROR', 'Упс, у нас какие-то проблемки при запросе к ИИ модели.')
TEXT_GENERAL_ERROR = os.environ.get('TEXT_GENERAL_ERROR', 'Произошла какая-то ошибка. Попробуй попозже, хорошо.')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            user_text = data.get("request", {}).get("command", "")
            version = data.get("version", "1.0")
            session = data.get("session", {})
            
            if not user_text:
                response = {
                    "response": {
                        "text": TEXT_NOT_UNDERSTOOD,
                        "tts": TEXT_NOT_UNDERSTOOD,
                        "end_session": False
                    },
                    "version": version
                }
            else:
                ai_response = self.get_ai_response(user_text)
                response = {
                    "response": {
                        "text": ai_response,
                        "tts": ai_response,
                        "end_session": False
                    },
                    "session": session,
                    "version": version
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"Ошибка: {e}")
            error_response = {
                "response": {
                    "text": TEXT_GENERAL_ERROR,
                    "tts": TEXT_GENERAL_ERROR,
                    "end_session": False
                },
                "version": "1.0"
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"status": "ok", "message": "Alice webhook is running"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def get_ai_response(self, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка при запросе к DeepSeek: {e}")
            return TEXT_DEEPSEEK_ERROR
