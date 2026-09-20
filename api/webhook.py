import os
import json
import httpx
from http.server import BaseHTTPRequestHandler

# Получаем API ключ из переменных окружения
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Обработка POST запросов от Алисы"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            # Извлекаем текст пользователя
            user_text = data.get("request", {}).get("command", "")
            
            if not user_text:
                response = {
                    "response": {
                        "text": "Я не поняла, что вы сказали. Повторите, пожалуйста.",
                        "tts": "Я не поняла, что вы сказали. Повторите, пожалуйста.",
                        "end_session": False
                    },
                    "version": data.get("version", "1.0")
                }
            else:
                # Получаем ответ от DeepSeek
                ai_response = self.get_ai_response(user_text)
                
                # Формируем ответ для Алисы
                response = {
                    "response": {
                        "text": ai_response,
                        "tts": ai_response,
                        "end_session": False
                    },
                    "session": data.get("session", {}),
                    "version": data.get("version", "1.0")
                }
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"Ошибка: {e}")
            error_response = {
                "response": {
                    "text": "Произошла ошибка. Попробуйте позже.",
                    "tts": "Произошла ошибка. Попробуйте позже.",
                    "end_session": False
                },
                "version": "1.0"
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """Обработка GET запросов (для проверки)"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"status": "ok", "message": "Alice webhook is running"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def get_ai_response(self, user_message: str) -> str:
        """Отправляет запрос в DeepSeek и возвращает ответ"""
        
        # Системный промпт для управления поведением ассистента
        system_prompt = "Ты полезный ассистент. Отвечай кратко и по делу на русском языке."
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
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
            return "Извините, произошла ошибка при обработке запроса."
