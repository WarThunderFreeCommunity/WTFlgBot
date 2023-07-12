import asyncio
import urllib
import requests
from typing import Literal, Optional

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

"""
self.return_back = nextcord.ui.Button(label="return_back")
async def return_back_callback(button, interaction):
    self.add_item(self.dropdown)
    self.remove_item(self.return_back)
    await self.message.edit(content=None, embed=self.embeds[0], view=self)
self.dropdown = nextcord.ui.Select(
    placeholder="Select the search result...",
    options=[
        nextcord.SelectOption(
            label=embed.title,
            description=embed.footer,
            value=self.embeds.index(embed)
        ) for embed in self.embeds[:25]
    ]
)
async def dropdown_callback(interaction):
    self.add_item(self.return_back)
    self.remove_item(self.dropdown)
    await self.message.edit(embed=self.embeds[self.dropdown.values[0]], view=self)
self.dropdown.callback = dropdown_callback 
self.add_item(self.dropdown)
"""

class AnimeView(nextcord.ui.View):
    def __init__(self, url, message):
        super().__init__(timeout=5*60)
        self.message = message
        self.url = urllib.parse.quote_plus(url)
        self.json = requests.get(f"https://api.trace.moe/search?url={self.url}").json()
        results = self.json["result"]
        main_embed = nextcord.Embed(
            title="Your search image"
        )
        main_embed.set_image(url)
        main_embed.set_footer(text=f"Searched {self.json['frameCount']} frames")
        self.embeds = [main_embed]
        for result in results:
            embed = nextcord.Embed(
                description=f"```Anilist: {result['anilist']}```"
                f"```Episode: {result['episode']}```"
                f"```Time: {self.convert_time_format(result['from'])} - {self.convert_time_format(result['to'])}```"
            )
            embed.set_author(name=result["filename"], url=result["video"])
            embed.set_image(result["image"])
            embed.set_footer(text=f"~{round(result['similarity']*100)}% Similarity")
            self.embeds.append(embed)
        self.return_back = nextcord.ui.Button(label="return_back")
        async def return_back_callback(interaction):
            self.add_item(self.dropdown)
            self.remove_item(self.return_back)
            await self.message.edit(content=None, embed=self.embeds[0], view=self)
        self.return_back.callback = return_back_callback
        self.dropdown = nextcord.ui.Select(
            placeholder="Select the search result...",
            options=[
                nextcord.SelectOption(
                    label=str(embed.author.name)[:100],
                    description=str(embed.footer.text),
                    value=self.embeds.index(embed)
                ) for embed in self.embeds[1:][:25]
            ]
        )
        async def dropdown_callback(interaction):
            self.add_item(self.return_back)
            self.remove_item(self.dropdown)
            await self.message.edit(embed=self.embeds[int(self.dropdown.values[0])], view=self)
        self.dropdown.callback = dropdown_callback 
        self.add_item(self.dropdown)
        self.on_init.start()

    @staticmethod
    def convert_time_format(time):
        minutes = int(time / 60)
        seconds = int(time % 60)
        milliseconds = int((time - int(time)) * 100)
        formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:02d}"
        return formatted_time

    @tasks.loop(count=1)
    async def on_init(self):
        await self.message.edit(content=None, embed=self.embeds[0], view=self)   

    async def on_timeout(self):
        await self.message.edit(content="timeout...", view=None)

class HelperCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        pass

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            "https://nextcord.gg/" in message.content
            and not message.author.guild_permissions.administrator
        ):
            for role_allowed in [
                nextcord.utils.find(
                    lambda r: r.id == 954393422716879019, message.guild.roles
                ),  # vip1 main
                nextcord.utils.find(
                    lambda r: r.id == 1007965606789783572, message.guild.roles
                ),  # vip2 main
                nextcord.utils.find(
                    lambda r: r.id == 827202390682894358, message.guild.roles
                ),  # deputy main
                nextcord.utils.find(
                    lambda r: r.id == 812667192104583218, message.guild.roles
                ),  # head main
                nextcord.utils.find(
                    lambda r: r.id == 1027862764322029679, message.guild.roles
                ),  # events main
            ]:
                if role_allowed in message.author.roles:
                    return
            await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.id == 159985870458322944 and message.channel.category_id in [
            851708687693119508,
            786488640087785492,
        ]:
            await message.delete()

    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        try:
            if "●" in before.channel.name and len(before.channel.members) == 0:
                await asyncio.sleep(60)
                channel = self.get_channel(before.channel.id)
                if channel is not None:
                    await channel.delete()
        except BaseException as e:
            pass

    @commands.command()
    async def image(self, ctx: Context, url: Optional[str] = None):
        if ctx.author.id not in self.bot.OWNERS and 814807573890465822 not in [role.id for role in ctx.author.roles]:
            return
        if "http" in url:
            message = await ctx.reply("loading...")
            view = AnimeView(url, message)
        else:
            await ctx.reply("неверный url")

# on_ready cog!
def setup(bot: Bot):
    print("HelperCog loaded!")
    bot.add_cog(HelperCog(bot))
