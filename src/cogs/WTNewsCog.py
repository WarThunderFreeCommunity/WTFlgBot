import time
import asyncio
from typing import List

import aiohttp
import requests
import nextcord
from bs4 import BeautifulSoup


RU_NEWS_HOOK = "https://discord.com/api/webhooks/1136742571457126410/DUwJQr-mg-KLYIjRbzK8MCcJ1PCwAXZ6x8M_UZ4JEGYUcsvLeQtJLmMjfGgF33izpkKr"
EN_NEWS_HOOK = ""
RU_CHANGES_HOOK = ""
EN_CHANGES_HOOK = ""


async def get_news_from_page(url):
    # Получаем код страницы
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ошибка при получении страницы. Код ошибки: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    news_blocks: List[BeautifulSoup] = soup.find_all(class_='showcase__item widget')
    
    news_data = []
    for block in news_blocks:
        title = block.find(class_='widget__title').text.strip()
        banner_url = block.find(
            class_='widget__poster-media js-lazy-load'
        )['data-src'].replace("//static", "https://static")
        comment = block.find(class_='widget__comment').text.strip()
        data = block.find(class_='widget-meta__item widget-meta__item--right').text.strip()
        more_url = "https://warthunder.com" + block.find(class_='widget__link')['href']
        
        #print(title)
        #print(banner_url)
        #print(data)
        #print(more_url)

        time.sleep(1)
        response = requests.get(more_url)
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении страницы. Код ошибки: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        p_tags = soup.find_all('p')
        #h2_tags = soup.find_all('h2')
        #all_tags = soup.find_all(['h2', 'p'])

        embed = nextcord.Embed(description=p_tags[0].text.strip())
        embed.set_author(name=title, url=more_url)
        embed.set_image(banner_url)

        async with aiohttp.ClientSession() as session:
            webhook = nextcord.Webhook.from_url(RU_NEWS_HOOK, session=session)
            await webhook.send(embed=embed)
        

if __name__ == "__main__":
    news_url = "https://warthunder.com/ru/news/"
    asyncio.run(get_news_from_page(news_url))






