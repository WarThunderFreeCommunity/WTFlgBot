from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

# MAIN

DEBUG: bool = os.getenv("DEBUG").lower() == "true"

