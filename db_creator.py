import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


async def main():
    db = DataBase("WarThunder.db")
    await db.connect()

    # Creating table in VKResendCog
    await db.run_que("CREATE TABLE IF NOT EXISTS VKResendCog (valId INTEGER)")
    ids = [8989, 8888, 8465, 4567, 1377, 1376, 1374, 1373, 1371, 1370]
    await db.run_que("INSERT INTO VKResendCog (valId) VALUES (?)", (json.dumps(ids),))
    # 1383, 1380
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
