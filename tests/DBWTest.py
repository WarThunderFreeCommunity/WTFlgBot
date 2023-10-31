import os
import sys
import unittest
from io import StringIO

import nest_asyncio

nest_asyncio.apply()

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "extensions"))
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.insert(0, src_path)
sys.path.insert(0, data_path)


from DBWorkerExtension import DataBase

CTX = None
events = []


class TestDataBase(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        events.append("setUp")

    def tearDown(self):
        events.append("tearDown")

    async def asyncSetUp(self):
        self.db = DataBase("test.db")
        await self.db.connect()

    async def asyncTearDown(self):
        await self.db.run_que("DROP TABLE IF EXISTS users")
        await self.db.close()
        file_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src", "data")
        )
        db_path = os.path.join(file_dir, "test.db")
        os.remove(db_path)
        #pass
    
    @unittest.skip("demonstrating skipping")
    async def test_create_table(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS usersnew (id INTEGER, name TEXT, age INTEGER)"
        )
        result = await self.db.get_all("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertIn(('usersnew',), result)

    async def test_create_table(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        result = await self.db.get_all("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertIn(('users',), result)

    async def test_add_user(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        await self.db.run_que(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (2, "John", 30)
        )
        result = await self.db.get_one("SELECT * FROM users WHERE id=?", (2,))
        self.assertEqual(result, (2, "John", 30))

    async def test_delete_user(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        await self.db.run_que(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", 
            [(1, "Alice", 25), (2, "Bob", 30)]
        )
        await self.db.run_que("DELETE FROM users WHERE id=?", (1,))
        result = await self.db.get_all("SELECT * FROM users")
        self.assertEqual(len(result), 1)

    async def test_get_users(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        await self.db.run_que(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", 
            [(1, "Alice", 25), (2, "Bob", 30)]
        )
        result = await self.db.get_all("SELECT * FROM users")
        self.assertEqual(len(result), 2)

    async def test_get_user_by_id(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        await self.db.run_que(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", 
            [(1, "Alice", 25), (2, "Bob", 30)]
        )
        result = await self.db.get_one("SELECT * FROM users WHERE id=?", (1,))
        self.assertEqual(result, (1, "Alice", 25))

    async def test_update_user_age(self):
        await self.db.run_que(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)"
        )
        await self.db.run_que(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", 
            [(1, "Alice", 25), (2, "Bob", 30)]
        )
        await self.db.run_que("UPDATE users SET age=? WHERE id=?", (26, 1))
        result = await self.db.get_one("SELECT * FROM users WHERE id=?", (1,))
        self.assertEqual(result[2], 26)


async def run_tests(**kwargs):
    print(info_str := f"```DBW TEST STARTED, kwargs:\n {kwargs}\n```")
    output_buffer = StringIO()

    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataBase)
    test_runner = unittest.TextTestRunner(stream=output_buffer)
    test_result = test_runner.run(test_suite)

    if kwargs.get("info"): info_str = info_str[:-3] + f"\n{output_buffer.getvalue()}```"

    return test_result, info_str


if __name__ == '__main__':
    unittest.main()
    #run_tests()
