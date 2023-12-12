from sqlalchemy import Column, Integer, String, Boolean

from core.database import Base


class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    news_url = Column(String, unique=False, index=True)
    title =  Column(String, unique=False, nullable=False)
    comment = Column(String, unique=False, nullable=False)
    date = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
