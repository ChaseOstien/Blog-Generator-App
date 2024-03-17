from db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import validates, relationship
from datetime import datetime



class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(5000), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user = relationship('User')

