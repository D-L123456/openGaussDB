import asyncio
import sys
sys.path.insert(0, r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend")

from app.core.database import async_session, init_db
from app.models.knowledge import KnowledgeNode

async def test():
    await init_db()
    async with async_session() as db:
        # Add a node
        node = KnowledgeNode(
            chapter="test",
            section="test",
            title="test_node_debug",
            content="original",
            sort_order=999,
        )
        db.add(node)
        await db.flush()
        node_id = str(node.id)
        print(f"Created node: {node_id}")

        # Try to get it
        found = await db.get(KnowledgeNode, node_id)
        print(f"Found by db.get: {found is not None}")
        if found:
            print(f"Content: {found.content}")
            found.content = "updated with images ![img](/images/test.png)"
            print(f"Updated content: {found.content}")

        await db.commit()

        # Verify after commit
        found2 = await db.get(KnowledgeNode, node_id)
        print(f"After commit content: {found2.content}")

        # Cleanup
        await db.delete(found2)
        await db.commit()

asyncio.run(test())