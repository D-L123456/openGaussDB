import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import async_session, init_db
from sqlalchemy import delete
from app.models.knowledge import KnowledgeNode
from app.services.knowledge_tree import knowledge_tree_service
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import vector_store

DOCX_DIR = r"C:\Users\11523\Desktop\教材文稿"


async def main():
    await init_db()

    async with async_session() as db:
        print("1. 清除旧知识树数据...")
        await db.execute(delete(KnowledgeNode))
        await db.commit()
        print("   已清除")

        print("2. 清除旧向量数据...")
        vector_store.reset()
        print("   已清除")

        print("3. 清除旧图片...")
        img_dir = os.path.join(os.path.dirname(__file__), "backend", "app", "data", "images")
        if os.path.exists(img_dir):
            for f in os.listdir(img_dir):
                os.remove(os.path.join(img_dir, f))
        os.makedirs(img_dir, exist_ok=True)
        print("   已清除")

        print("4. 重新提取文档（含图片）...")
        processor = DocumentProcessor()
        chunks = processor.extract_documents(DOCX_DIR)
        print(f"   提取到 {len(chunks)} 个文档块")

        print("5. 存入向量库...")
        count = vector_store.add_documents(chunks)
        print(f"   已存入 {count} 个向量")

        print("6. 构建知识树（含图片）...")
        result = await knowledge_tree_service.build_tree(DOCX_DIR, db)
        print(f"   知识树节点数: {result['total_nodes']}")

        print("7. 统计图片...")
        img_files = os.listdir(img_dir) if os.path.exists(img_dir) else []
        print(f"   提取图片数: {len(img_files)}")

        # 验证排序
        from sqlalchemy import select
        r = await db.execute(select(KnowledgeNode).where(KnowledgeNode.parent_id.is_(None)).order_by(KnowledgeNode.sort_order))
        roots = r.scalars().all()
        print("\n8. 章节排序验证:")
        for node in roots:
            print(f"   {node.title} (sort={node.sort_order})")

        print("\n完成！")

asyncio.run(main())
