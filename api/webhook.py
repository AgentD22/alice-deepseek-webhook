import os
import json
import re
import httpx
from http.server import BaseHTTPRequestHandler

# Настройки DeepSeek из переменных окружения Vercel
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "Ты полезный ассистент. Отвечай кратко и по делу на русском языке.",
)
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Настройки Telegram. Создайте эти переменные в Vercel:
# TELEGRAM_BOT_TOKEN — токен бота от @BotFather
# TELEGRAM_CHAT_ID — ID чата, куда отправлять ответы
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = "https://api.telegram.org"

# Тексты ответов
TEXT_NOT_UNDERSTOOD = os.environ.get(
    "TEXT_NOT_UNDERSTOOD", "Слушаю очень внимательно..."
)
TEXT_DEEPSEEK_ERROR = os.environ.get(
    "TEXT_DEEPSEEK_ERROR", "Извините, произошла ошибка при обработке запроса."
)
TEXT_GENERAL_ERROR = os.environ.get(
    "TEXT_GENERAL_ERROR", "Произошла ошибка. Попробуйте позже."
)

# Приветствие и команды
TEXT_WELCOME = os.environ.get(
    "TEXT_WELCOME", "О, привет! Я ваш настоящий ИИ ассистент. Счас буду тебе помогать?"
)
TEXT_GOODBYE = os.environ.get(
    "TEXT_GOODBYE", "Давай пока, еще увидимся думаю!."
)
TEXT_HELP = os.environ.get(
    "TEXT_HELP",
    'Я легко могу ответить на все твои вопросы. Задавай, а чтобы выйти, скажи "выход".',
)

EXIT_COMMANDS = ["выход", "выйти", "закрыть", "пока", "до свидания"]
HELP_COMMANDS = ["помощь", "помоги", "что ты умеешь", "команды"]

# Поддерживаем формулировки вроде:
# «Расскажи про Марс и отправь мне ответ в Telegram»
# «Сколько будет 2 + 2? Продублируй в телеграм»
TELEGRAM_REQUEST_PATTERNS = [
    re.compile(
        r"\b(?:и\s+)?(?:отправь|пришли|продублируй|скинь)\s+"
        r"(?:(?:мне|этот|ответ|это|его)\s+)*(?:в\s+)?"
        r"(?:телеграм(?:е)?|telegram)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:в\s+)?(?:телеграм(?:е)?|telegram)\s+"
        r"(?:мне\s+)?(?:отправь|пришли|продублируй|скинь)\b",
        re.IGNORECASE,
    ),
]


# Не выводим секретные значения в логи.
print("=" * 50)
print("Webhook запущен")
print(f"SYSTEM_PROMPT: {SYSTEM_PROMPT[:50]}...")
print(f"TEXT_NOT_UNDERSTOOD: {TEXT_NOT_UNDERSTOOD}")
print(f"Telegram настроен: {bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)}")
print("=" * 50)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            # Оставляем исходный регистр текста для DeepSeek; отдельно нормализуем
            # команду для проверки специальных команд навыка.
            user_text = data.get("request", {}).get("command", "").strip()
            normalized_command = user_text.lower().strip().rstrip(".!?,")
            version = data.get("version", "1.0")
            session = data.get("session", {})
            is_new_session = session.get("new", False)

            if is_new_session:
                response_text = TEXT_WELCOME
                end_session = False
            elif normalized_command in EXIT_COMMANDS:
                response_text = TEXT_GOODBYE
                end_session = True
            elif normalized_command in HELP_COMMANDS:
                response_text = TEXT_HELP
                end_session = False
            elif not user_text:
                response_text = TEXT_NOT_UNDERSTOOD
                end_session = False
            else:
                # Удаляем просьбу о пересылке из вопроса, чтобы DeepSeek отвечал
                # на сам вопрос, а не на инструкцию отправить его в Telegram.
                ai_prompt, send_to_telegram = self.extract_telegram_request(user_text)

                if not ai_prompt:
                    ai_prompt = (
                        "Пользователь просит отправить ответ в Telegram, "
                        "но не задал вопрос. Вежливо попроси его уточнить, "
                        "на какой вопрос нужно ответить."
                    )

                response_text = self.get_ai_response(ai_prompt)
                end_session = False

                # Отправляем в Telegram тот же готовый ответ, который получит Алиса.
                # Сбой Telegram не должен мешать ответу Алисы.
                if send_to_telegram:
                    try:
                        self.send_telegram_message(response_text)
                    except Exception:
                        # Ошибка HTTP может содержать URL с токеном бота — не логируем её целиком.
                        print("Не удалось отправить сообщение в Telegram; проверьте настройки и логи API.")

            response = {
                "response": {
                    "text": response_text,
                    "tts": response_text,
                    "end_session": end_session,
                },
                "session": session,
                "version": version,
            }
            self.send_json_response(response)

        except Exception as error:
            print(f"Ошибка обработки запроса: {error}")
            error_response = {
                "response": {
                    "text": TEXT_GENERAL_ERROR,
                    "tts": TEXT_GENERAL_ERROR,
                    "end_session": False,
                },
                "version": "1.0",
            }
            self.send_json_response(error_response)

    def do_GET(self):
        self.send_json_response(
            {
                "status": "ok",
                "message": "Alice webhook is running",
                "env_variables": {
                    "TEXT_NOT_UNDERSTOOD": TEXT_NOT_UNDERSTOOD,
                    "telegram_configured": bool(
                        TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
                    ),
                },
            }
        )

    def send_json_response(self, response):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))

    @staticmethod
    def extract_telegram_request(text: str):
        """Вернёт (текст для DeepSeek, нужно_ли_отправлять_ответ_в_Telegram)."""
        cleaned_text = text
        should_send = False

        for pattern in TELEGRAM_REQUEST_PATTERNS:
            cleaned_text, count = pattern.subn(" ", cleaned_text)
            if count:
                should_send = True

        if not should_send:
            return text, False

        # Убираем лишние союзы и знаки препинания, оставшиеся после удаления команды.
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        cleaned_text = re.sub(r"^(?:и|а)\s+", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s+(?:и|а)\s*$", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = cleaned_text.strip(" \t,.;:!?—-")

        return cleaned_text, True

    @staticmethod
    def send_telegram_message(text: str):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            raise RuntimeError(
                "Не заданы TELEGRAM_BOT_TOKEN и/или TELEGRAM_CHAT_ID в окружении"
            )

        # Telegram принимает не более 4096 символов в одном сообщении.
        telegram_text = text
        if len(telegram_text) > 4096:
            telegram_text = telegram_text[:4093] + "..."

        url = f"{TELEGRAM_API_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": telegram_text,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        if not result.get("ok"):
            # Не включаем URL или токен в текст ошибки/логи.
            raise RuntimeError("Telegram API отклонил отправку сообщения")

    @staticmethod
    def get_ai_response(user_message: str) -> str:
        if not DEEPSEEK_API_KEY:
            print("Не задана переменная окружения DEEPSEEK_API_KEY")
            return TEXT_DEEPSEEK_ERROR

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                return answer.strip() if answer else TEXT_DEEPSEEK_ERROR
        except Exception as error:
            print(f"Ошибка при запросе к DeepSeek: {error}")
            return TEXT_DEEPSEEK_ERROR
