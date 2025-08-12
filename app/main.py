from fastapi import FastAPI
from app.database import init_db
from app.routers import auth

# Основной роутер приложения
app = FastAPI()

# Обработчик старта приложения
@app.on_event("startup")
async def startup():
    await init_db()

# Подключаем маршруты аутентификации
app.include_router(auth.router, prefix="/auth")

# Корневая точка приложения
@app.get("/")
async def read_root():
    return {"message": "Добро пожаловать в службу аутентификации!"}