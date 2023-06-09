import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
import vk_api

from ..extensions.EXFormatExtension import format_exception, ex_format
from ..extensions.DBWorkerExtension import DataBase
from configuration import vk_servise_key, vk_app_id, vk_domain

class VKResendCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vk_update.start()

    @tasks.loop(seconds=5)
    async def vk_update(self):
        try:
            vk_session = vk_api.VkApi(app_id=vk_app_id, token=vk_servise_key)
            vk = vk_session.get_api()
            self.wall = vk.wall.get(domain=vk_domain, count=1)

            id = self.wall['items'][-1]['id']
            db = DataBase("WarThunder.db")
            await db.connect()
            if (await db.get_one("SELECT * FROM VKResendCog WHERE valId=?", (id,))) == None:
                #print(await db.get_all("SELECT * FROM VKResendCog"))
                await db.run_que('INSERT INTO VKResendCog (valId) VALUES (?)', (id,))

                avatar_author = 'https://sun9-24.userapi.com/impg/S0g9s8KKftuqPX3dIBHHY2jw8tgGtnC4x-i9Jg/azI1ProULmg.jpg?size=512x512&quality=95&sign=c5ee033441f41cf2ac4e2d057f6d2df6&type=album'
                channel_id = 1114216573901754459

                all = self.get_all()

                url_post, text_post, photos, videos = all['url'], all['text'], all['photo'], all['videos']
                if len(videos) > 0:
                    videos_links = "\n".join([f"[link_to_video]({post})" for post in videos])
                else:
                    videos_links = ""
                embed_main = nextcord.Embed.from_dict({
                    "description": f"{text_post} \n {videos_links}",
                    "url": photos[0],
                    "color": 0xE74C3C,
                    "author": {
                        "name": "War Thunder Events",
                        "url": url_post,
                        "icon_url": avatar_author
                    },
                    "image": {
                        "url": photos[0]
                    },
                })

                channel = self.bot.get_channel(channel_id)
                embeds_list = []
                embeds_list.append(embed_main)
                if len(photos) > 1:
                    for photo in photos[1:]:
                        embed = nextcord.Embed()
                        embed.url = photo
                        embed.set_image(photo)
                        embeds_list.append()

                await channel.send(embeds=embeds_list)

            else:
                print('This id is already in table')
        except BaseException as ex:
            print(ex_format(ex, "vk_update"))
            pass
        finally:
            await db.close()




    def get_videos(self, items: dict):
        list = []
        length = len(items)
        for number in range(length):
            try:
                video = f"https://vk.com/video{items[1]['video']['owner_id']}_{items[number]['video']['id']}"
                list.append(video)
            except:
                pass
        return list

    def get_number_res(self, items: list):
        count = len(items)+1
        for number in range(count):
            type = items[number]['type']
            if type == 'x':
                photo_url = items[number]['url']
                return photo_url
        return items[0]['width']

    def get_photos(self, items: dict):
        list = []
        length = len(items)
        items = items
        for number in range(length):
            try:
                photo = self.get_number_res(items[number]['photo']['sizes'])
                list.append(photo)
            except:
                pass
        return list

    def get_all(self):
        try:
            items = self.wall['items'][0]
            # print(items['owner_id'], items['post_id'])
            text = items['text']
            text = f"*{text}*"

            attachments = items['attachments']
            url = f"https://vk.com/wall{self.wall['items'][-1]['owner_id']}_{self.wall['items'][-1]['id']}"
            photo = self.get_photos(attachments)
            videos = self.get_videos(attachments)
            return {'url': url, 'text': text, 'videos': videos, 'photo': photo}
        except:
            pass
    # async def create(self, ctx: Context):
    #     await ctx.send("test", view=PersistentView())


# on_ready cog!
def setup(bot: Bot):
    print("VKResendCog loaded!")
    bot.add_cog(VKResendCog(bot))
