from typing import Literal

from pydantic import BaseModel, Field


class AgentAnalysis(BaseModel):
    level: Literal["OPTIMO", "ATENCION", "CRITICO", "SIN_DATOS"]
    confidence: Literal["Baja", "Media", "Alta"]

    headline: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    evidence: list[str] = Field(default_factory=list)
    probable_causes: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    priority: Literal["BAJA", "MEDIA", "ALTA", "CRITICA"]
    requires_human_review: bool = False
