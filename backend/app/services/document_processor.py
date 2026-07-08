import os
import re
import hashlib
from dataclasses import dataclass

import docx
from lxml import etree
from app.core.config import settings

NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images")


def natural_sort_key(s: str) -> list:
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return [convert(c) for c in re.split(r'(\d+)', s)]


def extract_images_from_para(para, doc, chapter_name, para_idx) -> list[str]:
    image_refs = []
    blips = para._element.findall('.//a:blip', NSMAP)
    for blip in blips:
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if not rid:
            continue
        try:
            rel = doc.part.rels[rid]
            image_blob = rel.target_part.blob
            content_type = rel.target_part.content_type
            ext_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/tiff': '.tiff',
                'image/x-emf': '.emf',
                'image/x-wmf': '.wmf',
            }
            ext = ext_map.get(content_type, '.png')
            img_hash = hashlib.md5(image_blob).hexdigest()[:12]
            img_filename = f"{chapter_name}_{para_idx}_{img_hash}{ext}"
            img_path = os.path.join(IMAGES_DIR, img_filename)
            if not os.path.exists(img_path):
                os.makedirs(IMAGES_DIR, exist_ok=True)
                with open(img_path, 'wb') as f:
                    f.write(image_blob)
            image_refs.append(f"[图片: /images/{img_filename}]")
        except Exception:
            pass
    return image_refs


def clean_figure_references(text: str) -> str:
    text = re.sub(r'如[图图]\s*\d+[\.\d]*\s*所[示述]', '', text)
    text = re.sub(r'[见参看][图图]\s*\d+[\.\d]*', '', text)
    text = re.sub(r'[上下]图\s*\d+[\.\d]*', '', text)
    text = re.sub(r'图\s*\d+[\.\d]*\s*[所示]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


@dataclass
class DocumentChunk:
    chapter: str
    section: str
    title: str
    content: str
    metadata: dict


class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_documents(self, docx_dir: str | None = None) -> list[DocumentChunk]:
        doc_dir = docx_dir or settings.docx_dir
        if not doc_dir:
            raise ValueError("未配置文档目录，请设置DOCX_DIR环境变量")

        chunks: list[DocumentChunk] = []
        files = sorted([f for f in os.listdir(doc_dir) if f.endswith(".docx")], key=natural_sort_key)

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

        for para_idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            image_refs = extract_images_from_para(para, doc, chapter_name, para_idx)

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
                parts_to_add = []
                if image_refs:
                    parts_to_add.extend(image_refs)
                if text:
                    cleaned = clean_figure_references(text)
                    if cleaned:
                        parts_to_add.append(cleaned)
                if parts_to_add:
                    current_content_parts.extend(parts_to_add)

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
