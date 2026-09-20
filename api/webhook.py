import os
import json
import httpx
from http.server import BaseHTTPRequestHandler

# Получаем настройки из переменных окружения
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
SYSTEM_PROMPT = os.environ.get('SYSTEM_PROMPT', 'Ты полезный ассистент. Отвечай кратко и по делу на русском языке.')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Тексты ответов
TEXT_NOT_UNDERSTOOD = os.environ.get('TEXT_NOT_UNDERSTOOD', 'Я не поняла, что вы сказали. Повторите, пожалуйста.')
TEXT_DEEPSEEK_ERROR = os.environ.get('TEXT_DEEPSEEK_ERROR', 'Извините, произошла ошибка при обработке запроса.')
TEXT_GENERAL_ERROR = os.environ.get('TEXT_GENERAL_ERROR', 'Произошла ошибка. Попробуйте позже.')

# Приветствие и команды
TEXT_WELCOME = os.environ.get('TEXT_WELCOME', 'О, привет! Я ваш настоящий ИИ ассистент. Счас буду тебе помогать?')
TEXT_GOODBYE = os.environ.get('TEXT_GOODBYE', 'Давай пока, еще увидимся думаю!.')
TEXT_HELP = os.environ.get('TEXT_HELP', 'Я легко могу ответить на все твои вопросы. Задавай, а чтобы выйти, скажи "выход".')

# Команды для выхода и помощи (можно настроить)
EXIT_COMMANDS = ['выход', 'выйти', 'закрыть', 'пока', 'до свидания']
HELP_COMMANDS = ['помощь', 'помоги', 'что ты умеешь', 'команды']

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            user_text = data.get("request", {}).get("command", "").lower().strip()
            version = data.get("version", "1.0")
            session = data.get("session", {})
            
            # Проверяем, это новый сеанс (первое сообщение)
            is_new_session = data.get("session", {}).get("new", False)
            
            # Определяем ответ
            if is_new_session:
                # Приветствие при первом запуске
                response_text = TEXT_WELCOME
                end_session = False
            elif user_text in EXIT_COMMANDS:
                # Команда выхода
                response_text = TEXT_GOODBYE
                end_session = True
            elif user_text in HELP_COMMANDS:
                # Команда помощи
                response_text = TEXT_HELP
                end_session = False
            elif not user_text:
                # Пустой запрос
                response_text = TEXT_NOT_UNDERSTOOD
                end_session = False
            else:
                # Обычный запрос к DeepSeek
                response_text = self.get_ai_response(user_text)
                end_session = False
            
            # Формируем ответ
            response = {
                "response": {
                    "text": response_text,
                    "tts": response_text,
                    "end_session": end_session
                },
                "session": session,
                "version": version
            }
            
            # Отправляем ответ
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
