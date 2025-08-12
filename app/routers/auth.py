from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select
from jose import JWSError
from app.schemas import (
    UserCreate,
    UserInDB,
    PasswordResetRequest,
    UserLogin,
    ResetPasswordForm
)
from app.database import get_session
from app.models import User
from app.utils.jwt_utils import (
    create_access_token,
    decode_jwt_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    RESET_TOKEN_EXPIRE_MINUTES
)
from app.utils.email_utils import send_reset_password_email
import logging

# Настройки логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Роутер для работы с аутентификацией
router = APIRouter()

# Контекст шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для сравнения паролей
async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Генерация хешированного пароля
async def get_password_hash(password):
    return pwd_context.hash(password)

# Регистрация пользователя
@router.post("/register", response_model=UserInDB)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_session)
):
    """
    Регистрирует нового пользователя в системе.
    """
    hashed_password = await get_password_hash(user.password)
    try:
        new_user = User(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=hashed_password
        )
        db.add(new_user)
        await db.commit()
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с такими данными уже зарегистрирован."
        )

# Вход в аккаунт
@router.post("/login")
async def login(request_body: UserLogin, db: AsyncSession = Depends(get_session)):
    """
    Авторизирует пользователя и возвращает JWT-токен.
    """
    username = request_body.username
    password = request_body.password
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо ввести имя пользователя и пароль."
        )
    user_query = await db.execute(select(User).where(User.username == username))
    user = user_query.scalars().first()
    if not user or not await verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидные учётные данные.")
    token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

# Запрос восстановления пароля
@router.post("/password-reset-request")
async def request_password_reset(
        request_body: PasswordResetRequest,
        db: AsyncSession = Depends(get_session),
):
    """
    Генерирует ссылку для сброса пароля и отправляет её на почту пользователя.
    """
    username = request_body.username
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Требуется указать имя пользователя."
        )
    user_query = await db.execute(select(User).where(User.username == username))
    user = user_query.scalars().first()
    if not user:
        return {"message": f"Отправлено уведомление на электронную почту."}
    token_data = {
        "sub": user.id,
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    }
    reset_token = create_access_token(token_data)
    await send_reset_password_email(email=user.email, reset_token=reset_token, reset_url="http://localhost:8000/reset-password")
    return {"message": "Инструкция по восстановлению пароля отправлена на почтовый ящик."}

# Смена пароля по токену
@router.post("/reset-password")
async def reset_password(reset_form: ResetPasswordForm, db: AsyncSession = Depends(get_session)):
    """
    Восстанавливает пароль пользователя, используя полученный токен.
    """
    token = reset_form.token
    new_password = reset_form.new_password
    try:
        payload = decode_jwt_token(token)
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный токен."
            )
        user_query = await db.execute(select(User).where(User.id == user_id))
        user = user_query.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден."
            )
        hashed_password = await get_password_hash(new_password)
        user.hashed_password = hashed_password
        await db.commit()
        return {"message": "Пароль успешно восстановлен."}
    except JWSError:
        raise HTTPException(status_code=401, detail="Ошибка проверки токена.")
    except Exception as e:
        logger.error(f"Ошибка при восстановлении пароля: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")