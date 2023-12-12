from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")

