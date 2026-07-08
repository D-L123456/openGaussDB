import os
import logging

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import vector_store
from app.services.knowledge_tree import knowledge_tree_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

_ingestion_running = False


@router.post("/ingest")
async def ingest_documents(
    background_tasks: BackgroundTasks,
    docx_dir: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    global _ingestion_running
    if _ingestion_running:
        return {"status": "already_running", "message": "文档导入正在进行中"}

    _ingestion_running = True

    async def run_ingestion():
        global _ingestion_running
        try:
            dir_path = docx_dir or settings.docx_dir
            if not dir_path:
                logger.error("未配置文档目录")
                return

            processor = DocumentProcessor()
            chunks = processor.extract_documents(dir_path)
            logger.info(f"提取到 {len(chunks)} 个文档块")

            count = await vector_store.add_documents(chunks)
            logger.info(f"已存入 {count} 个向量")

            await knowledge_tree_service.build_tree(dir_path, db)
            logger.info("知识树构建完成")

        except Exception as e:
            logger.error(f"文档导入失败: {e}")
        finally:
            _ingestion_running = False

    background_tasks.add_task(run_ingestion)
    return {"status": "started", "message": "文档导入已启动"}


@router.get("/ingest/status")
async def ingestion_status():
    return {"running": _ingestion_running}


@router.post("/reset")
async def reset_knowledge_base(db: AsyncSession = Depends(get_db)):
    vector_store.reset()
    return {"status": "reset", "message": "知识库已重置"}