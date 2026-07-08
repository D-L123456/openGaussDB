import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app.core.database import async_session, init_db
from sqlalchemy import select
from app.models.knowledge import KnowledgeNode

async def main():
    await init_db()
    async with async_session() as db:
        r = await db.execute(select(KnowledgeNode).where(KnowledgeNode.parent_id.is_(None)).order_by(KnowledgeNode.sort_order))
        roots = r.scalars().all()
        print(f"Root nodes: {len(roots)}")
        for n in roots:
            print(f"  sort={n.sort_order}: {n.title}")

asyncio.run(main())