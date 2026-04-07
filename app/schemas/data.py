from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class AnalysisRequestMetadata(BaseModel):
    user_id: Optional[str] = None
    channel: Optional[str] = "web"


class AnalysisRequest(BaseModel):
    text: str
    source: str = "user_submission"
    metadata: Optional[AnalysisRequestMetadata] = None


class AnalysisRequestBody(BaseModel):
    request: AnalysisRequest


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


# Data injection schemas
class CaseCreate(BaseModel):
    description: str
    fraud_type: Optional[str] = None
    amount: Optional[float] = None
    keywords: List[str] = []


class CaseCreateRequest(BaseModel):
    case: CaseCreate


class TipCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    keywords: List[str] = []


class TipCreateRequest(BaseModel):
    tip: TipCreate
