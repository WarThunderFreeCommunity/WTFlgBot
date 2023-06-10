import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


async def main():
    db = DataBase("WarThunder.db")
    await db.connect()

    # Creating table in VKResendCog
    await db.run_que("CREATE TABLE IF NOT EXISTS VKResendCog (valId INTEGER)")
    ids = [1344, 1341, 1339, 1338, 1337, 1234, 5432, 6357, 3457, 7643]
    await db.run_que("INSERT INTO VKResendCog (valId) VALUES (?)", (json.dumps(ids),))
    
    await db.close()


if __name__ == "__main__":
    print("Настройки для тестового сервера")
    asyncio.run(main())
