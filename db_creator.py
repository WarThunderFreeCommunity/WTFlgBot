import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


async def main():
    db = DataBase("WarThunder.db")
    await db.connect()
  
  
    await db.close()
    
    


if __name__ == "__main__":
    print("Настройки для тестового сервера")
    asyncio.run(main())
