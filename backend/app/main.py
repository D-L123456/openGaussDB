import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api import chat, sql_practice, knowledge_tree, admin, recommendations, learning
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "data", "images")
DOCX_DIR = r"C:\Users\11523\Desktop\教材文稿"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    await init_db()

    logger.info("加载向量数据...")
    count = vector_store.load_from_documents(DOCX_DIR)
    logger.info(f"向量数据加载完成: {count} 个向量")

    yield
    logger.info("关闭应用")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(sql_practice.router)
app.include_router(knowledge_tree.router)
app.include_router(admin.router)
app.include_router(recommendations.router)
app.include_router(learning.router)

os.makedirs(IMAGES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }