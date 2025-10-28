from typing import List, Literal
from pydantic import BaseModel

class ExtractedSkill(BaseModel):
    skill: str
    score: float
    evidence_offsets: List[List[int]] = []
    aliases_matched: List[str] = []

class GapItem(BaseModel):
    skill: str
    priority: int

class Critique(BaseModel):
    summary: str
    bullets: List[str]
    tone: Literal["supportive","direct"] = "supportive"

class ExtractionResponse(BaseModel):
    resume_id: str
    extract_id: str
    role: str
    skills: List[ExtractedSkill]
    gaps: List[GapItem]
    critique: Critique
    text_preview: str
    model_ver: str
