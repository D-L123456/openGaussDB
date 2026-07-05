from pydantic import BaseModel


class KnowledgeNodeResponse(BaseModel):
    id: str
    parent_id: str | None = None
    chapter: str
    section: str
    title: str
    content: str | None = None
    sort_order: int = 0
    children: list["KnowledgeNodeResponse"] = []

    model_config = {"from_attributes": True}


class KnowledgeTreeResponse(BaseModel):
    nodes: list[KnowledgeNodeResponse]


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class KnowledgeSearchResult(BaseModel):
    node_id: str
    chapter: str
    section: str
    title: str
    content: str
    score: float
