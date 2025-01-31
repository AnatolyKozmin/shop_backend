import sys
import os
sys.path.append(os.getcwd())

from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship




class Raiting(Base):
    __tablename__ = 'raitings'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)
    #reviews = Column(String, ForeignKey('reviews.id'))
    

    
