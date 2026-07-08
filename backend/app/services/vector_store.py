import logging
from typing import Optional

import chromadb
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self._chroma_client = chromadb.Client()
        self._embed_collection = self._chroma_client.get_or_create_collection("embed-helper")

    def _encode(self, texts: list[str]) -> list[list[float]]:
        self._embed_collection.upsert(ids=[f"q{i}" for i in range(len(texts))], documents=texts)
        results = self._embed_collection.get(ids=[f"q{i}" for i in range(len(texts))], include=["embeddings"])
        self._chroma_client.delete_collection("embed-helper")
        self._embed_collection = self._chroma_client.get_or_create_collection("embed-helper")
        return results["embeddings"]

    def _get_conn(self):
        import psycopg2
        dsn = settings.database_url
        if "+asyncpg" in dsn:
            dsn = dsn.replace("+asyncpg", "")
        return psycopg2.connect(dsn)

    async def add_documents(self, chunks: list) -> int:
        return self._add_documents_sync(chunks)

    def _add_documents_sync(self, chunks: list) -> int:
        if not chunks:
            return 0
        conn = self._get_conn()
        cur = conn.cursor()
        inserted = 0
        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk.chapter}_{chunk.section}_{i}"
            emb = self._encode([chunk.content])[0]
            emb_str = "[" + ",".join(str(v) for v in emb) + "]"
            cur.execute(
                """INSERT INTO knowledge_chunks (id, chapter, section, title, content, chunk_type, embedding)
                   VALUES (%s, %s, %s, %s, %s, %s, %s::vector) ON CONFLICT (id) DO NOTHING""",
                (chunk_id, chunk.chapter, chunk.section, chunk.title, chunk.content,
                 chunk.metadata.get("type", "text"), emb_str)
            )
            inserted += 1
        conn.commit()
        cur.close()
        conn.close()
        return inserted

    async def search(self, query: str, top_k: int = 5, chapter_filter: Optional[str] = None) -> list[dict]:
        return self._search_sync(query, top_k, chapter_filter)

    def _search_sync(self, query: str, top_k: int = 5, chapter_filter: Optional[str] = None) -> list[dict]:
        query_emb = self._encode([query])[0]
        emb_str = "[" + ",".join(str(v) for v in query_emb) + "]"

        conn = self._get_conn()
        cur = conn.cursor()

        if chapter_filter:
            cur.execute(
                """SELECT content, chapter, section, title, chunk_type,
                          1 - (embedding <=> %s::vector) AS similarity
                   FROM knowledge_chunks
                   WHERE chapter LIKE %s
                   ORDER BY embedding <=> %s::vector
                   LIMIT %s""",
                (emb_str, f"%{chapter_filter}%", emb_str, top_k)
            )
        else:
            cur.execute(
                """SELECT content, chapter, section, title, chunk_type,
                          1 - (embedding <=> %s::vector) AS similarity
                   FROM knowledge_chunks
                   ORDER BY embedding <=> %s::vector
                   LIMIT %s""",
                (emb_str, emb_str, top_k)
            )

        results = []
        for row in cur.fetchall():
            results.append({
                "content": row[0],
                "metadata": {
                    "chapter": row[1],
                    "section": row[2],
                    "title": row[3],
                    "type": row[4],
                },
                "score": float(row[5]),
            })

        cur.close()
        conn.close()
        return results

    async def get_all_metadata(self) -> list[dict]:
        return self._get_all_metadata_sync()

    def _get_all_metadata_sync(self) -> list[dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT chapter, section, title FROM knowledge_chunks")
        results = [{"chapter": r[0], "section": r[1], "title": r[2]} for r in cur.fetchall()]
        cur.close()
        conn.close()
        return results

    def count(self) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM knowledge_chunks WHERE embedding IS NOT NULL")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count

    def reset(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("TRUNCATE knowledge_chunks")
        conn.commit()
        cur.close()
        conn.close()

    def load_from_documents(self, docx_dir: str | None = None) -> int:
        return self.count()


vector_store = VectorStore()
