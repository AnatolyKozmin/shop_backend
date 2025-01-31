import sys # Нужно для того, чтобы мы могли нормально имортировать модели ниже
import os
sys.path.append(os.getcwd())

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_session_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session 
        
