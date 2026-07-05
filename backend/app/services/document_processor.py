import os
import re
from dataclasses import dataclass

import docx
from app.core.config import settings


@dataclass
class DocumentChunk:
    chapter: str
    section: str
    title: str
    content: str
    metadata: dict


class DocumentProcessor:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def extract_documents(self, docx_dir: str | None = None) -> list[DocumentChunk]:
        doc_dir = docx_dir or settings.docx_dir
        if not doc_dir:
            raise ValueError("未配置文档目录，请设置DOCX_DIR环境变量")

        chunks: list[DocumentChunk] = []
        files = sorted([f for f in os.listdir(doc_dir) if f.endswith(".docx")])

        for filename in files:
            filepath = os.path.join(doc_dir, filename)
            doc = docx.Document(filepath)
            chapter_name = filename.replace(".docx", "")
            file_chunks = self._parse_document(doc, chapter_name)
            chunks.extend(file_chunks)

        return chunks

    def _parse_document(self, doc: docx.Document, chapter_name: str) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        current_section = ""
        current_title = ""
        current_content_parts: list[str] = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            style_name = para.style.name if para.style else ""

            if "Heading 1" in style_name:
                if current_content_parts:
                    content = "\n".join(current_content_parts)
                    chunks.extend(self._split_content(
                        chapter_name, current_section, current_title, content
                    ))
                current_section = text
                current_title = text
                current_content_parts = []
            elif "Heading 2" in style_name:
                if current_content_parts:
                    content = "\n".join(current_content_parts)
                    chunks.extend(self._split_content(
                        chapter_name, current_section, current_title, content
                    ))
                current_section = text
                current_title = text
                current_content_parts = []
            elif "Heading 3" in style_name:
                if current_content_parts:
                    content = "\n".join(current_content_parts)
                    chunks.extend(self._split_content(
                        chapter_name, current_section, current_title, content
                    ))
                current_title = text
                current_content_parts = [text]
            else:
                current_content_parts.append(text)

        if current_content_parts:
            content = "\n".join(current_content_parts)
            chunks.extend(self._split_content(
                chapter_name, current_section, current_title, content
            ))

        for table in doc.tables:
            table_text = self._extract_table(table)
            if table_text.strip():
                chunks.append(DocumentChunk(
                    chapter=chapter_name,
                    section=current_section,
                    title=f"{current_title} - 表格",
                    content=table_text,
                    metadata={"type": "table"}
                ))

        return chunks

    def _extract_table(self, table) -> str:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            rows.append(" | ".join(cells))
        return "\n".join(rows)

    def _split_content(
        self, chapter: str, section: str, title: str, content: str
    ) -> list[DocumentChunk]:
        if len(content) <= self.chunk_size:
            return [DocumentChunk(
                chapter=chapter,
                section=section,
                title=title,
                content=content,
                metadata={"type": "text"}
            )]

        chunks = []
        start = 0
        while start < len(content):
            end = start + self.chunk_size
            chunk_text = content[start:end]

            if end < len(content):
                last_period = max(
                    chunk_text.rfind("。"),
                    chunk_text.rfind("；"),
                    chunk_text.rfind("\n"),
                )
                if last_period > self.chunk_size // 2:
                    chunk_text = chunk_text[: last_period + 1]
                    end = start + last_period + 1

            chunks.append(DocumentChunk(
                chapter=chapter,
                section=section,
                title=title,
                content=chunk_text.strip(),
                metadata={"type": "text", "chunk_index": len(chunks)}
            ))
            start = end - self.chunk_overlap

        return chunks