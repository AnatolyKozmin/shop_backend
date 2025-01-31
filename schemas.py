from pydantic import BaseModel
from sqlalchemy import DateTime

class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int

class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    
class CreateRewiev(BaseModel):
    comment: str 
    raiting: int
    #comment_date: DateTime # Сомнительная хуйня 


class CreateRaiting(BaseModel):
    grade: float 

