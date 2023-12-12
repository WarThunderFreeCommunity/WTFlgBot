from sqlalchemy import Column, Integer, String, Boolean

from core.database import Base


class News(Base):
    __tablename__ = "news"
    
    news_url = Column(String, primary_key=True, index=True)
    title =  Column(String, unique=True, nullable=False)
    comment = Column(String, unique=True, nullable=False)
    date = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
