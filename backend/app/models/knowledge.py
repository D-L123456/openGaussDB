import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=True)
    chapter: Mapped[str] = mapped_column(String(50))
    section: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parent: Mapped["KnowledgeNode | None"] = relationship(remote_side="KnowledgeNode.id", back_populates="children")
    children: Mapped[list["KnowledgeNode"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
