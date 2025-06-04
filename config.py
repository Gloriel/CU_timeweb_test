import os
from dotenv import load_dotenv

# Загружаем .env только если он есть (локально)
load_dotenv()

# Берём токен из переменной окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не задан. Установите переменную BOT_TOKEN в .env или через системные переменные.")