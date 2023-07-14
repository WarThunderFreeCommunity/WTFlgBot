import os
import aeval
import asyncio

import aiosqlite

try:
    from .EXFormatExtension import ex_format
except ImportError:
    from EXFormatExtension import ex_format

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
        self.connected: bool = False
    
    async def debug_dbase(self, command, inter, view=None, db=None):
        """_summary_
        
        Args:
            command (_type): _description_
            inter (_type): _description_
            view (_type): _description_. Defaults to []
            db (_type): _description_. Defaults to []
        """
        try:
            await self.run_que(command, inter)
        except:
            await aeval.aeval(command, standart_args, {})

    async def connect(self):
        """_summary_
        """
        try:
            self.db_connection = await aiosqlite.connect(self.db_path)
            self.connected = True
        except BaseException as ex:
            print(ex_format(ex, "connect"))

    async def close(self):
        """_summary_
        """
        try:
            if self.connected:
                await self.db_connection.close()
                self.connected = False
            else:
                raise "sqlite db not conected!"
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
            print(ex_format(ex, f"run_que, {sql}"))
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
    import json
    db = DataBase("WarThunder.db")
    await db.connect()
    parrent_channel_ids = {
        '1119276330253566042': 'RU:T:SB:1119287140585582723',
        '1119287140585582723': 'RU:A:SB:-',
        '1119276441952063518': 'RU:T:RB:1119276522000367676',
        '1119276522000367676': 'RU:A:RB:-',
        '1119276788422561802': 'RU:T:AB:1119276934061375608',
        '1119276934061375608': 'RU:A:AB:-',
        '1119277201704099860': 'RU:S:SH:1119277285531451564', # морские 
        '1119277285531451564': 'RU:H:HE:-', # вертолёты
        '1119277359158276166': 'RU:P:PO:1119357957893799937', # полигон
        '1119357957893799937': 'RU:O:OP:-', # общалка
        '1119363801561714830': 'EN:T:SB:1119363908415791174',
        '1119363908415791174': 'EN:A:SB:-',
        '1119364907868115065': 'EN:T:RB:1119364910753792201',
        '1119364910753792201': 'EN:A:RB:-',
        '1119366275265724577': 'EN:T:AB:1119366324745932810',
        '1119366324745932810': 'EN:A:AB:-',
        '1119366554337951744': 'EN:S:SH:1119366610738741269', # морские 
        '1119366610738741269': 'EN:H:HE:-', # вертолёты
        '0000000000000000000': 'EN:P:PO:0000000000000000000', # полигон
        '0000000000000000000': 'EN:O:OP:-' # общалка
    }
    await db.run_que(
        "UPDATE VoiceCogConstants SET constantValue=? WHERE constantName=?",
        (json.dumps(parrent_channel_ids), "parrent_channel_ids")
    )
    await db.close()


if __name__ == "__main__":
    asyncio.run(__test())