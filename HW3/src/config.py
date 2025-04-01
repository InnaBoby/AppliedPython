import os
from dotenv import load_dotenv

load_dotenv()

DB_USER=os.getenv('DB_USER')
DB_PASS=os.getenv('DB_PASS')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_NAME=os.getenv('DB_NAME')

REDIS_URL=os.getenv('REDIS_URL')

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')