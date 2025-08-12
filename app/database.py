import asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession
)
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import logging
from sqlalchemy.orm import sessionmaker

# Настраиваем логгер
logger = logging.getLogger(__name__)

# URL базы данных
DATABASE_URL = "postgresql+asyncpg://admin:admin@db/auth_db"

# Создаем движок базы данных
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Заводим фабрику сессий
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

# Базовый класс модели
Base = declarative_base()

# Генератор асинхронных сессий
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session

# Ждем готовности базы данных
async def wait_for_db():
    while True:
        try:
            async with engine.begin() as conn:
                break
        except Exception as e:
            print(f"Ждём подключения к базе данных: {e}")
            await asyncio.sleep(5)

# Инициализация базы данных
async def init_db():
    await wait_for_db()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Инициализация базы данных выполнена успешно.")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {str(e)}")
        raise