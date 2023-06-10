import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
import vk_api

from ..extensions.EXFormatExtension import format_exception, ex_format
from ..extensions.DBWorkerExtension import DataBase
from configuration import vk_servise_key, vk_app_id, vk_domain

# TODO sending skipped messages
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

            id = self.wall["items"][-1]["id"]
            db = DataBase("WarThunder.db")
            await db.connect()
            if (
                await db.get_one("SELECT * FROM VKResendCog WHERE valId=?", (id,))
            ) == None:
                # print(await db.get_all("SELECT * FROM VKResendCog"))
                # await db.run_que('UPDATE VKResendCog SET valId=? WHERE valId=?', (id,))

                avatar_author = "https://sun9-24.userapi.com/impg/S0g9s8KKftuqPX3dIBHHY2jw8tgGtnC4x-i9Jg/azI1ProULmg.jpg?size=512x512&quality=95&sign=c5ee033441f41cf2ac4e2d057f6d2df6&type=album"
                channel_id = 1114216573901754459

                all = self.get_all()

                url_post, text_post, photos, videos = (
                    all["url"],
                    all["text"],
                    all["photo"],
                    all["videos"],
                )
                if len(videos) > 0:
                    videos_links = "\n".join(
                        [f"[link_to_video]({post})" for post in videos]
                    )
                else:
                    videos_links = ""
                embed_main = nextcord.Embed.from_dict(
                    {
                        "description": f"{text_post} \n {videos_links}",
                        "url": photos[0],
                        "color": 0xE74C3C,
                        "author": {
                            "name": "War Thunder Events",
                            "url": url_post,
                            "icon_url": avatar_author,
                        },
                        "image": {"url": photos[0]},
                    }
                )

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
                print("This id is already in table")
        except BaseException as ex:
            print(ex_format(ex, "vk_update"))
            pass
        finally:
            await db.close()

    def get_videos(self, attachments: dict):
        result_list = []
        for item in attachments:
            try:
                video = f"https://vk.com/video{item['video']['owner_id']}_{item['video']['id']}"
                result_list.append(video)
            except:
                pass
        return result_list

    def get_number_res(self, items: list):
        for item in items:
            if item["type"] == "x":
                photo_url = item["url"]
                return photo_url
        return items[0]["width"]

    def get_photos(self, attachments: dict):
        photos = []
        for item in attachments:
            try:
                photo = self.get_number_res(item["photo"]["sizes"])
                photos.append(photo)
            except BaseException:
                pass
        return photos

    def get_all(self):
        for item in self.wall["items"]:
            text = item["text"]
            attachments = item["attachments"]

            url = f"https://vk.com/wall{item['owner_id']}_{item['id']}"
            photo = self.get_photos(attachments)
            videos = self.get_videos(attachments)
            z = {"url": url, "text": text, "videos": videos, "photo": photo}



# on_ready cog!
def setup(bot: Bot):
    print("VKResendCog loaded!")
    bot.add_cog(VKResendCog(bot))
