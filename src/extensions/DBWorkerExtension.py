import os
import asyncio

import aiosqlite

from .EXFormatExtension import ex_format


class DataBase:
    def __init__(self, db_name):
        """_summary_

        Args:
            db_name (_type_): _description_
        """
        file_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        self.db_path = os.path.join(file_dir, db_name)
        self.db_connection = None
    
    async def connect(self):
        """_summary_
        """
        try:
            self.db_connection = await aiosqlite.connect(self.db_path)
        except BaseException as ex:
            print(ex_format(ex, "connect"))

    async def close(self):
        """_summary_
        """
        try:
            await self.db_connection.close()
        except BaseException as ex:
            print(ex_format(ex, "close"))

    async def run_que(self, sql, params=None):
        """run - запрос нихуя не возвращает

        Args:
            sql (_type_): _description_
            params (list, optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """
        try:
            async with self.db_connection.cursor() as cursor:
                if isinstance(params, list):
                    await cursor.executemany(sql, params)
                else:
                    await cursor.execute(sql, params)
                await self.db_connection.commit()
            return {"id": cursor.lastrowid}
        except BaseException as ex:
            print(ex_format(ex, "run_que"))
            return False

    async def get_one(self, sql, params=None):
        """get - возврат строки

        Args:
            sql (_type_): _description_
            params (list, optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """
        try:
            async with self.db_connection.execute(sql, params) as cursor:
                return await cursor.fetchone()
        except BaseException as ex:
            print(ex_format(ex, "get_one"))
            return False

    async def get_all(self, sql, params=None):
        """all - возврат массива строк

        Args:
            sql (_type_): _description_
            params (list, optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """
        try:
            async with self.db_connection.execute(sql, params) as cursor:
                return await cursor.fetchall()
        except BaseException as ex:
            print(ex_format(ex, "get_all"))
            return False


# Пример создания таблицы
async def __create_table():
    db = DataBase("example.db")
    await db.connect()
    await db.run_que("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)")
    await db.close()

# Пример добавления значения
async def __add_user():
    db = DataBase("example.db")
    await db.connect()
    await db.run_que("INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (2, "John", 30))
    await db.close()

# Пример удаления значения
async def __delete_user():
    db = DataBase("example.db")
    await db.connect()
    await db.run_que("DELETE FROM users WHERE id=?", (1,))
    await db.close()

# Пример выборки значений
async def __get_users():
    db = DataBase("example.db")
    await db.connect()
    result = await db.get_all("SELECT * FROM users")
    await db.close()
    return result

# Пример выборки одного значения
async def __get_user_by_id(user_id):
    db = DataBase("example.db")
    await db.connect()
    result = await db.get_one("SELECT * FROM users WHERE id=?", (user_id,))
    await db.close()
    return result

# Пример обновления значения
async def __update_user_age(user_id, new_age):
    db = DataBase("example.db")
    await db.connect()
    await db.run("UPDATE users SET age=? WHERE id=?", (new_age, user_id))
    await db.close()


async def __test():
    db = DataBase("WarThunder.db")
    await db.connect()
    ...
    await db.close()


if __name__ == "__main__":
    asyncio.run(__test())