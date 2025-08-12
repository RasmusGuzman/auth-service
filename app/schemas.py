from pydantic import BaseModel, EmailStr, validator
from pydantic.types import constr
from typing import Optional
import re

# Валидатор пароля
def validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError('Пароль должен содержать минимум 8 символов.')
    if not re.search(r'[a-z]', v):
        raise ValueError('Пароль должен содержать строчную букву.')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Пароль должен содержать заглавную букву.')
    if not re.search(r'[0-9]', v):
        raise ValueError('Пароль должен содержать цифру.')
    if not re.search(r'[@$!%*?&]', v):
        raise ValueError('Пароль должен содержать спецсимвол.')
    return v

# Форма для сброса пароля
class ResetPasswordForm(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        return validate_password(v)

    @validator('confirm_password')
    def check_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают.')
        return v

# Данные для регистрации пользователя
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20)
    password: str
    email: EmailStr
    phone: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        return validate_password(v)

# Пользовательская информация в базе данных
class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: Optional[str] = None
    hashed_password: str

    class Config:
        orm_mode = True

# Вход пользователя
class UserLogin(BaseModel):
    username: str
    password: str

# Запрос на восстановление пароля
class PasswordResetRequest(BaseModel):
    username: str
