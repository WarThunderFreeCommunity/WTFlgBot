import json
import aiohttp
import datetime

import vk_api
import nextcord
from nextcord.ext import tasks
from nextcord.ext.commands import Bot, Cog

from ..extensions.EXFormatExtension import ex_format
from ..extensions.DBWorkerExtension import DataBase
from configuration import vk_app_id, vk_servise_key, avatar_author

# TODO sending skipped messages
class VKResendCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vk_update.start()

    def get_videos(self, attachments: dict):
        result_list = []
        for attachment in attachments:
            try:
                video = f"https://vk.com/video{attachment['video']['owner_id']}_{attachment['video']['id']}"
                result_list.append(video)
            except BaseException:
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
        for attachment in attachments:
            try:
                photo = self.get_number_res(attachment["photo"]["sizes"])
                photos.append(photo)
            except BaseException:
                pass
        return photos

    @tasks.loop(minutes=10)
    async def vk_update(self):
        try:
            vk_session = vk_api.VkApi(app_id=vk_app_id, token=vk_servise_key)
            vk = vk_session.get_api()
            wall = vk.wall.get(domain="warthunderevents", count=10)

            DB =  DataBase("WarThunder.db")
            await DB.connect()
            last_id_posts = await DB.get_one("SELECT * FROM VKResendCog")
            last_id_posts = json.loads(last_id_posts[0])
            await DB.run_que("DELETE FROM VKResendCog")
            await DB.run_que("INSERT INTO VKResendCog (valId) VALUES (?)", (json.dumps([item['id'] for item in wall["items"] ]),))

            for item in wall["items"][::-1]:
                if item['id'] in last_id_posts:
                    continue

                attachments = item["attachments"]
                url = f"https://vk.com/wall{item['owner_id']}_{item['id']}"
                text = item["text"]
                photos = self.get_photos(attachments)
                videos = self.get_videos(attachments)
                post_time = datetime.datetime.fromtimestamp(int(item['date']))#Вывод даты и времени



                vk_tags = {
                    "#история@warthunderevents": "https://discord.com/api/webhooks/1116993460516429914/kNBfNlNqalyfPT"
                        "wkl4Z37xruoHoBw9mq0Jszner5ij8gmJV0qpD7FS5qCMjCxzA9igKh", # wt main
                    "#видео@warthunderevents": "https://discord.com/api/webhooks/1116993460516429914/kNBfNlNqalyfPTwkl"
                        "4Z37xruoHoBw9mq0Jszner5ij8gmJV0qpD7FS5qCMjCxzA9igKh", # wt main
                    "#events_discord@warthunderevents" : "https://discord.com/api/webhooks/1117022288768929812/ZEVph6B"
                        "sY2YWasAedLte_42YMwYiiyTbfW8SXSvqFhD_p6GGHw_GkHeu99c8EF45Lhcv",# wt events
                    "#конкурс@warthunderevents" : "https://discord.com/api/webhooks/1117022288768929812/ZEVph6BsY2YWasA"
                        "edLte_42YMwYiiyTbfW8SXSvqFhD_p6GGHw_GkHeu99c8EF45Lhcv",  # wt events
                    "#CDK@warthunderevents" : "https://discord.com/api/webhooks/1117021162313109544/16LCbmNEmhnkSITdgPJ"
                        "RZrE9PC3dWC2dtT95nVHBtVo6cSn2n7bRIBETH5bV_8Eel65c", # cdk
                } # TODO: Возможна фича с двойной отправкой в один канал, если указываешь два тега идущие к одному вебхуку
                used_hoocks = {}

                for vk_tag in vk_tags:
                    if vk_tag in text and used_hoocks.get(item['id']) != vk_tags[vk_tag]:
                        if len(text) > 3500:
                            text = text[:3500] + f"\n[Текст был обрезан, оригинал смотрите в группе]({url})"

                        embeds = []
                        # TODO: Можно заменить ссылку на видео на имя видео
                        try:
                            videos_links = "\n".join(
                                [f"[Ссылка на видео]({video})" for video in videos]
                            ) if len(videos) > 0 else ""
                            photos_link = "\n".join( 
                                [f"[Ссылка на фото вне поста]({photo})" for photo in photos[4:]]
                            ) if (len(photos) > 4 and len(photos) > 0) else ""
                        except BaseException as ex:
                            print(ex)
                            videos_links = ""
                            photos_link = ""
                        embed_main = nextcord.Embed.from_dict(
                            {
                                "description": f"{text} \n {videos_links} \n {photos_link}",
                                "url": photos[0],
                                "color": 0xFF2E2E,
                                "author": {
                                    "name": "War Thunder Events",
                                    "url": url,
                                    "icon_url": avatar_author,
                                },
                                "image": {"url": photos[0]},
                            }
                        )
                        embed_main.set_footer(text="Имя паблика кликабельно, ссылка ведёт на пост. Гиперссылки - не поместившиеся картинки или видео.")
                        embed_main.timestamp = post_time  # Вывод даты и времени
                        embeds.append(embed_main)
                        if len(photos) > 1:
                            for photo in photos[1:4]:
                                embed = nextcord.Embed()
                                embed.url = photos[0]
                                embed.set_image(photo)
                                embeds.append(embed)

                    
                        used_hoocks[item['id']] = vk_tags[vk_tag]
                        async with aiohttp.ClientSession() as session:
                            webhook = nextcord.Webhook.from_url(vk_tags[vk_tag], session=session)
                            await webhook.send(embeds=embeds)                
        except BaseException as ex:
            print(ex_format(ex, "vk_update"))
        finally:
            await DB.close()


# on_ready cog!
def setup(bot: Bot):
    print("VKResendCog loaded!")
    bot.add_cog(VKResendCog(bot))
