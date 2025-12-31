"""
FastAPI приложение для админ-панели
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .auth import verify_admin_token, create_admin_token
from .routes.products import router as products_router
from .routes.orders import router as orders_router
from .routes.upload import router as upload_router
from .routes.dashboard import router as dashboard_router
from .routes.public_products import router as public_products_router
from ..database import db

def create_admin_app() -> FastAPI:
    """Создать FastAPI приложение для админки"""
    
    app = FastAPI(
        title="Telegram Shop Admin API",
        description="API для управления интернет-магазином",
        version="1.0.0",
        docs_url="/admin/docs",
        redoc_url="/admin/redoc"
    )
    
    # CORS для фронтенда
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключение к базе при старте
    @app.on_event("startup")
    async def startup_event():
        """Подключение к базе данных при запуске приложения"""
        await db.connect()
    
    @app.on_event("shutdown") 
    async def shutdown_event():
        """Отключение от базы данных при завершении работы приложения"""
        await db.disconnect()
    
    # Роуты API
    # Подключение роутов админ-панели
    app.include_router(products_router, prefix="/admin/api", tags=["products"])
    app.include_router(orders_router, prefix="/admin/api", tags=["orders"])
    app.include_router(upload_router, prefix="/admin/api", tags=["upload"])
    app.include_router(dashboard_router, prefix="/admin/api", tags=["dashboard"])

    # Публичные роуты для веб-приложения
    app.include_router(public_products_router, prefix="/api", tags=["public"])
    
    # Аутентификация
    @app.post("/admin/api/auth/login")
    async def login(credentials: dict):
        """Авторизация админа"""
        from ..config import settings
        
        username = credentials.get("username")
        password = credentials.get("password")
        
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            token = create_admin_token(username)
            return {"access_token": token, "token_type": "bearer"}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    @app.get("/admin/api/auth/me")
    async def get_current_user(token: str = Depends(verify_admin_token)):
        """Получить текущего пользователя"""
        return {"username": "admin", "role": "administrator"}
    
    # Статические файлы React (если собраны)
    frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
    if os.path.exists(frontend_dist):
        app.mount("/admin", StaticFiles(directory=frontend_dist, html=True), name="admin")
    
    @app.get("/")
    async def root():
        return {"message": "Telegram Shop API", "admin_panel": "/admin"}
    
    return app