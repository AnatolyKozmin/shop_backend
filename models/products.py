import sys
import os
sys.path.append(os.getcwd())

from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float  
from sqlalchemy.orm import relationship 
from app.models.user import User

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    supplier_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id')) 
    
    rating = Column(Float)
    
    is_active = Column(Boolean, default=True)

    category = relationship('Category', back_populates='products') 
    reviews = relationship('Review', back_populates='products')
