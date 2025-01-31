from fastapi import APIRouter, Depends, status, HTTPException
#from fastapi.security import HTTPBasic, HTTPBasicCredentials Использовалось для базовой аутентификации 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy import insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession 
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError

from app.models.user import User
from app.schemas import CreateUser
from app.backend.dp_depends import get_db

SECRET_KEY = 'a21679097c1ba42e9bd06eea239cdc5bf19b249e87698625cba5e3572f005544'
ALGORITHM = 'HS256'

router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
f'''
Всё то, что здесь закомментировано, это была базовая аутентификация на основе HTTP Basic Security 
В переделанном варианте используется Oauth2 и JWT токены
'''
#security = HTTPBasic()
# async def get_current_username(db: Annotated[AsyncSession, Depends(get_db)], credentials: HTTPBasicCredentials = Depends(security)):
#     user = await db.scalar(select(User).where(User.username == credentials.username))
#     if not user or not bcrypt_context.verify(credentials.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#         )
#     return user

# @router.get('/users/me')
# async def read_current_user(user: dict = Depends(get_current_username)):
#     return {'User': user}
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication creditials',
            headers={'WWWW-Authenticate': 'Bearer'}
            )
    
    return user

async def create_access_token(username: str, user_id: int, is_admin: bool, 
                              is_supplier: bool, is_customer: bool, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 
              'is_admin': is_admin, 'is_supplier': is_supplier,
              'is_custumer': is_customer}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str= payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: str = payload.get('is_admin')
        is_supplier: str = payload.get('is_suppler')
        is_customer: str = payload.get('is_custumer')
        expire = payload.get('exp')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Noaccess token supplied'
            )
        return {
            'username': username,
            'id': user_id,
            'is_admin': is_admin, 
            'is_supplier': is_supplier,
            'is_customer': is_customer
        }
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            deetail='Token expired !'
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    await db.execute(insert(User).values(first_name=create_user.first_name,
                                         last_name=create_user.last_name,
                                         username=create_user.username,
                                         email=create_user.email,
                                         hashed_password=bcrypt_context.hash(create_user.password),
                                      ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'

        }


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)

    token = await create_access_token(user.username, 
                                      user.id, 
                                      user.is_admin, 
                                      user.is_supplier, 
                                      user.is_customer,
                                      expires_delta=timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@router.get('/read_current_user')
async def read_current_user(user: User = Depends(get_current_user)):
    return user