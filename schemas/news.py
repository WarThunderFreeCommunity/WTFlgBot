from pydantic import BaseModel


class NewsInDB(BaseModel):
    news_url: str
    title: str
    comment: str
    date: str
    image_url: str
