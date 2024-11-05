import logging
import logging.config
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.user import user_router
from app.configs.settings import settings
from app.configs.mysql import init_db
from starlette.middleware.sessions import SessionMiddleware
from app.configs.redis import redis_client
import os


# Logging Settings
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Application 시작")
    try:
        app.state.redis = await redis_client.connect()
        await init_db()
        logger.info("데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {str(e)}", exc_info=True)
        raise

    yield
    # Shutdown event
    await redis_client.disconnect()
    logger.info("Application 종료")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # CORS Settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    # API router
    api_router = APIRouter(prefix="/api")

    # Routers
    api_router.include_router(user_router.router, prefix="/users", tags=["users"])

    # Health Check Endpoint
    @app.get("/health", tags=["Health Check"])
    def health_check():
        return {"status": "ok"}

    @app.get("/redis-test")
    async def redis_test():
        try:
            await app.state.redis.set("test", "success")
            result = await app.state.redis.get("test")
            return {"redis": result}
        except Exception as e:
            logger.error(f"Redis error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Redis connection error")

    static_dir = "app/static"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app


app = create_app()

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
