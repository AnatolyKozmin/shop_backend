import sys
import os 
sys.path.append(os.getcwd())

from sqlalchemy import Column, Boolean, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship 

from app.backend.db import Base
from app.models.products import Product


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=True) # Покупатель может поставить только оценку
    comment_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)

    raiting = relationship('Raiting', back_populates='Rewievs')

    

    




