from typing import List

import requests
from bs4 import BeautifulSoup

def get_news_from_page(url):
    # Получаем код страницы
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ошибка при получении страницы. Код ошибки: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    news_blocks: List[BeautifulSoup] = soup.find_all(class_='showcase__item widget')
    
    news_data = []
    for block in news_blocks:
        title = block.find(class_='widget__title').text.strip()
        banner_url = block.find(class_='widget__poster-media js-lazy-load')['data-src']
        comment = block.find(class_='widget__comment').text.strip()
        data = block.find(class_='widget-meta__item widget-meta__item--right').text.strip()
        more_url = "warthunder.com" + block.find(class_='widget__link')['href']
        print(banner_url)
        print(more_url)
        return

if __name__ == "__main__":
    news_url = "https://warthunder.ru/ru/news/"
    news_list = get_news_from_page(news_url)





