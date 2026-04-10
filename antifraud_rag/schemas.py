from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    text: str
    source: str = "user_submission"


class MatchedCase(BaseModel):
    case_id: UUID
    description: str
    confidence: float
    fraud_type: Optional[str] = None
    key_indicators: List[str] = []


class DirectHitData(BaseModel):
    risk_level: str = "HIGH"
    matched_cases: List[MatchedCase]
    recommended_action: str = "停止一切操作，立即报警"


class RAGPromptContext(BaseModel):
    relevant_cases: List[Dict[str, Any]]
    anti_fraud_tips: List[Dict[str, Any]]


class RAGPromptData(BaseModel):
    risk_level: str = "MEDIUM"
    rrf_score: float
    prompt: str
    context: RAGPromptContext


class AnalysisResponse(BaseModel):
    status: str = "success"
    result_type: str  # "Direct_Hit" or "RAG_Prompt"
    data: Union[DirectHitData, RAGPromptData]
