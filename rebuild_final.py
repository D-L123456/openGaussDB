import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import async_session, init_db
from sqlalchemy import delete, select
from app.models.knowledge import KnowledgeNode
from app.services.knowledge_tree import knowledge_tree_service

DOCX_DIR = r"C:\Users\11523\Desktop\教材文稿"


async def main():
    await init_db()

    async with async_session() as db:
        print("1. 清除旧知识树数据...")
        await db.execute(delete(KnowledgeNode))
        await db.commit()
        print("   已清除")

        print("2. 构建知识树（不清除图片，复用已有）...")
        result = await knowledge_tree_service.build_tree(DOCX_DIR, db)
        print(f"   知识树节点数: {result['total_nodes']}")

        print("3. 统计图片...")
        img_dir = os.path.join(os.path.dirname(__file__), "backend", "app", "data", "images")
        img_files = os.listdir(img_dir) if os.path.exists(img_dir) else []
        print(f"   图片数: {len(img_files)}")

        print("4. 验证图片引用...")
        r = await db.execute(select(KnowledgeNode).where(KnowledgeNode.content.like("%/images/%")))
        img_nodes = r.scalars().all()
        print(f"   含图片的节点数: {len(img_nodes)}")

        print("5. 章节排序验证:")
        r = await db.execute(select(KnowledgeNode).where(KnowledgeNode.parent_id.is_(None)).order_by(KnowledgeNode.sort_order))
        roots = r.scalars().all()
        for node in roots:
            print(f"   {node.title} (sort={node.sort_order})")

        print("\n完成！")

asyncio.run(main())