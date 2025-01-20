from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

# Чтение токена из переменной окружения
BOT_TOKEN=os.getenv('BOT_TOKEN')
OPEN_WEATHER_API_KEY=os.getenv('OPEN_WEATHER_API_KEY')

if not BOT_TOKEN:
    raise ValueError('Переменная окружения BOT_TOKEN не установлена!')