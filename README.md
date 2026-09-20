# 🧠 Алиса + DeepSeek — Голосовой AI-ассистент

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Serverless-black?logo=vercel&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM-green?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiIGZpbGw9IiMwMGYwZmYiLz48L3N2Zz4=)
![Yandex Alice](https://img.shields.io/badge/Yandex-Alice-purple?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiIGZpbGw9IiNmZjAwMDAiLz48L3N2Zz4=)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Умная колонка Яндекс Алиса, работающая через нейросеть DeepSeek**

[О проекте](#-о-проекте) • [Архитектура](#-архитектура) • [Быстрый старт](#-быстрый-старт) • [Настройка](#-настройка)

</div>

---

## 📖 О проекте

Этот проект позволяет умной колонке **Яндекс Алиса** отвечать на вопросы пользователей, используя мощь нейросети **DeepSeek** вместо встроенных алгоритмов Яндекса.

Проще говоря — Алиса становится **намного умнее** 🚀

### Что умеет:

- 🗣️ Отвечать на любые вопросы через DeepSeek
- 🧠 Помнить контекст разговора
- ⚡ Быстро обрабатывать запросы через serverless-архитектуру
- 🔒 Безопасно хранить API-ключи в переменных окружения
- 🔄 Автоматически обновляться при каждом push в GitHub

---

## 🏗 Архитектура

```
┌─────────────┐     ┌─────────────────┐     ┌───────────────┐
│   🎤 Алиса   │────▶│  ☁️ Vercel       │────▶│  🧠 DeepSeek  │
│  (колонка)   │◀────│  (Webhook API)   │◀────│    (LLM API)  │
└─────────────┘     └────────┬────────┘     └───────────────┘
                             │
                             │ auto-deploy
                             ▼
                    ┌─────────────────┐
                    │  🐙 GitHub       │
                    │  (репозиторий)   │
                    └─────────────────┘
```

### Как это работает:

1. **Пользователь** задаёт вопрос колонке Алиса
2. **Алиса** отправляет запрос на webhook в Vercel
3. **Vercel** пересылает вопрос в DeepSeek API
4. **DeepSeek** генерирует умный ответ
5. **Vercel** возвращает ответ Алисе
6. **Алиса** озвучивает ответ пользователю

---

## 🛠 Технологии

| Технология | Назначение |
|---|---|
| **Python** | Язык программирования webhook-сервера |
| **Vercel** | Serverless-платформа для хостинга webhook |
| **DeepSeek API** | Нейросеть для генерации ответов |
| **GitHub** | Хранение кода и CI/CD |
| **Яндекс Диалоги** | Платформа для создания навыков Алисы |

---

## 🚀 Быстрый старт

### Что вам понадобится:

- Аккаунт на [GitHub](https://github.com)
- Аккаунт на [Vercel](https://vercel.com)
- API-ключ [DeepSeek](https://platform.deepseek.com)
- Аккаунт разработчика [Яндекс Диалоги](https://dialogs.yandex.ru)

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/ВАШ_ЛОГИН/alice-deepseek-webhook.git
cd alice-deepseek-webhook
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустите локально для тестирования

```bash
python api/webhook.py
```

Webhook будет доступен на `http://localhost:8000/api/webhook`

---

## ⚙️ Настройка

### Переменные окружения

Создайте файл `.env` в корне проекта или настройте переменные в Vercel:

| Переменная | Описание | Пример |
|---|---|---|
| `DEEPSEEK_API_KEY` | API-ключ от DeepSeek | `sk-xxxxxxxxxxxx` |
| `DEEPSEEK_MODEL` | Модель DeepSeek | `deepseek-chat` |
| `SYSTEM_PROMPT` | Системный промпт для AI | `Ты — дружелюбный ассистент` |
| `TEXT_NOT_UNDERSTOOD` | Фраза при ошибке | `Слушаю тебя внимательно!` |
| `MAX_TOKENS` | Макс. длина ответа | `500` |
| `TEMPERATURE` | Креативность (0-1) | `0.7` |

### Развёртывание на Vercel

1. **Импортируйте проект** из GitHub в Vercel
2. **Настройте переменные окружения** в Settings → Environment Variables
3. **Деплой** произойдёт автоматически

После деплоя ваш webhook будет доступен по адресу:

```
https://ваш-проект.vercel.app/api/webhook
```

### Подключение к Яндекс Алисе

1. Зайдите на [dialogs.yandex.ru](https://dialogs.yandex.ru)
2. Создайте новый **навык**
3. В настройках укажите:
   - **Тип backend**: Webhook
   - **Webhook URL**: `https://ваш-проект.vercel.app/api/webhook`
4. Пройдите модерацию
5. Опубликуйте навык и привяжите к колонке

---

## 📁 Структура проекта

```
alice-deepseek-webhook/
├── api/
│   └── webhook.py          # Основной обработчик webhook
├── requirements.txt        # Зависимости Python
├── vercel.json             # Конфигурация Vercel
└── README.md               # Этот файл
```

---

## 🔧 Кастомизация

### Изменение системного промпта

Вы можете настроить поведение AI, изменив переменную `SYSTEM_PROMPT`:

```
# Дружелюбный помощник
SYSTEM_PROMPT = "Ты — дружелюбный голосовой ассистент. Отвечай кратко и по делу."

# Эксперт по cooking
SYSTEM_PROMPT = "Ты — шеф-повар с 20-летним опытом. Помогай с рецептами."

# Пират 🏴‍☠️
SYSTEM_PROMPT = "Ты — весёлый пират. Отвечай в пиратском стиле, матрос!"
```

### Смена модели DeepSeek

Измените переменную `DEEPSEEK_MODEL`:

- `deepseek-chat` — быстрая модель для обычных задач
- `deepseek-reasoner` — модель с рассуждениями для сложных задач

---

## 🐛 Решение проблем

| Проблема | Решение |
|---|---|
| Алиса не отвечает | Проверьте URL webhook в настройках навыка |
| Ошибка "TEXT_NOT_UNDERSTOOD" | Проверьте API-ключ DeepSeek |
| Долгий ответ | Уменьшите `MAX_TOKENS` или `TEMPERATURE` |
| Деплой не проходит | Проверьте логи в Vercel → Deployments |

---

## 📝 Лицензия

MIT License — используйте свободно! 🎉

---

<div align="center">

**Сделано с ❤️ и помощью ИИ [Qwen](https://qwen.ai)**

Если проект понравился — поставьте ⭐

</div>
