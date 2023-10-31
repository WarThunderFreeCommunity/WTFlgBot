import os
import sys
import unittest
from io import StringIO

import nextcord
from nextcord.ext import commands, tasks
import nest_asyncio

nest_asyncio.apply()

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_path)

BOT: commands.Bot = None
CTX: commands.Context = None
events = []


class TestServerStats(unittest.IsolatedAsyncioTestCase):
    
    @classmethod
    def setUpClass(cls):
        global BOT
        cls.bot = BOT
        voice_members = set()

        guild = cls.bot.get_guild(1075733298371899433)
        online = len(
            list(filter(lambda x: x.status == nextcord.Status.online, guild.members))
        )
        idle = len(
            list(filter(lambda x: x.status == nextcord.Status.idle, guild.members))
        )
        dnd = len(
            list(filter(lambda x: x.status == nextcord.Status.dnd, guild.members))
        )

        for voice in guild.voice_channels:
            for member in voice.members:
                voice_members.add(member.id)

        cls.current_online = online + idle + dnd
        cls.current_voices_online = len(voice_members)
        cls.current_all_members = len(guild.members)
        cls.current_games = 0

    @staticmethod
    def is_within_10_percent(num1, num2):
        if num1 == num2:
            return True

        percent_difference = abs(num1 - num2) / max(abs(num1), abs(num2)) * 100

        return percent_difference <= 10
    
    def test_equal_numbers(self):
        self.assertTrue(self.is_within_10_percent(5, 5))
        self.assertTrue(self.is_within_10_percent(0, 0))
        self.assertTrue(self.is_within_10_percent(-10, -10))

    def test_within_10_percent(self):
        self.assertTrue(self.is_within_10_percent(100, 110))
        self.assertTrue(self.is_within_10_percent(50, 45))
        self.assertTrue(self.is_within_10_percent(-20, -18))

    def test_not_within_10_percent(self):
        self.assertFalse(self.is_within_10_percent(100, 120))
        self.assertFalse(self.is_within_10_percent(50, 55)) # 56
        self.assertFalse(self.is_within_10_percent(-20, -15))

    def test_zero_division(self):
        self.assertTrue(self.is_within_10_percent(0, 0))
        self.assertFalse(self.is_within_10_percent(0, 1))
        self.assertFalse(self.is_within_10_percent(1, 0))

    async def test_current_online(self):
        online = int(
            self.bot.get_channel(1143333714437357579).name.split("-")[-1:][0]
        )  # online
        self.assertEqual(self.is_within_10_percent(online, self.current_online), True)

    async def test_all_members_count(self):
        members = int(
            self.bot.get_channel(1143333689015685120).name.split("-")[-1:][0]
        )  # members
        self.assertEqual(
            self.is_within_10_percent(members, self.current_all_members), True
        )

    async def test_in_voices_members(self):
        voice = int(
            self.bot.get_channel(1143592654517575741).name.split("-")[-1:][0]
        )  # voice
        self.assertEqual(
            self.is_within_10_percent(voice, self.current_voices_online), True
        )

    async def test_current_games(self):
        games = int(
            self.bot.get_channel(1143333745311617154).name.split("-")[-1:][0]
        )  # games
        self.assertEqual(self.is_within_10_percent(games, self.current_games), True)


async def run_tests(**kwargs):
    global BOT, CTX
    BOT = kwargs.get("bot")
    CTX = kwargs.get("thread")

    print(info_str := f"```SRVSTAT TEST STARTED, kwargs:\n {kwargs}\n```")
    output_buffer = StringIO()

    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestServerStats)
    test_runner = unittest.TextTestRunner(stream=output_buffer)
    test_result = test_runner.run(test_suite)

    if kwargs.get("info"):
        info_str = info_str[:-3] + f"\n{output_buffer.getvalue()}```"
    if len(info_str) >= 2000:
        info_str = info_str[:1990] + "\n...```"

    return test_result, info_str


if __name__ == "__main__":
    unittest.main()
    # run_tests(bot="123")
