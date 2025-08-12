from fastapi import HTTPException
from jose import jwt, JWSError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем секретный ключ и алгоритм шифрования
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES"))

# Логируем полученные ключи
logger.info(f"SECRET_KEY: {SECRET_KEY}, ALGORITHM: {ALGORITHM}")

# Функция для создания JWT-токенов
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Создает JWT-токен с указанным сроком действия.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Ошибка при создании токена: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка создания токена")

# Функция для декодирования JWT-токенов
def decode_jwt_token(token: str):
    """
    Декодирует JWT-токен и возвращает полезную нагрузку.
    """
    try:
        if not SECRET_KEY or not ALGORITHM:
            raise ValueError("Не найдены необходимые переменные окружения")
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except JWSError as jwe:
        logger.error(f"Ошибка JWT: {str(jwe)}")
        raise HTTPException(status_code=401, detail="Ошибка проверки токена")
    except ValueError as ve:
        logger.error(f"Ошибка значения: {str(ve)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail="Произошла внутренняя ошибка")