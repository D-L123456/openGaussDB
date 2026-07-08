import logging
import os
from typing import Optional

import chromadb
from app.core.config import settings
from app.services.document_processor import DocumentChunk

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._loaded = False

    def add_documents(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk.chapter}_{chunk.section}_{i}"
            ids.append(chunk_id)
            documents.append(chunk.content)
            metadatas.append({
                "chapter": chunk.chapter,
                "section": chunk.section,
                "title": chunk.title,
                "type": chunk.metadata.get("type", "text"),
            })

        batch_size = 100
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

        return len(ids)

    def search(self, query: str, top_k: int = 5, chapter_filter: Optional[str] = None) -> list[dict]:
        where_filter = None
        if chapter_filter:
            where_filter = {"chapter": {"$contains": chapter_filter}}

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()) if self.collection.count() > 0 else top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                search_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": 1 - results["distances"][0][i] if results["distances"] else 0.0,
                })

        return search_results

    def get_all_metadata(self) -> list[dict]:
        results = self.collection.get(include=["metadatas"])
        if not results or not results["metadatas"]:
            return []

        seen = set()
        unique_metadata = []
        for meta in results["metadatas"]:
            key = f"{meta.get('chapter', '')}_{meta.get('section', '')}_{meta.get('title', '')}"
            if key not in seen:
                seen.add(key)
                unique_metadata.append(meta)

        return unique_metadata

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        self.client.delete_collection(settings.chroma_collection_name)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._loaded = False

    def load_from_documents(self, docx_dir: str | None = None) -> int:
        if self._loaded and self.collection.count() > 0:
            return self.collection.count()

        doc_dir = docx_dir or settings.docx_dir
        if not doc_dir or not os.path.exists(doc_dir):
            logger.warning(f"文档目录不存在: {doc_dir}")
            return 0

        logger.info(f"从文档加载向量数据: {doc_dir}")
        from app.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        chunks = processor.extract_documents(doc_dir)
        count = self.add_documents(chunks)
        self._loaded = True
        logger.info(f"已加载 {count} 个向量")
        return count


vector_store = VectorStore()