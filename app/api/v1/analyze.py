import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.data import (
    AnalysisRequestBody,
    AnalysisResponse,
    DirectHitData,
    MatchedCase,
    RAGPromptContext,
    RAGPromptData,
)
from app.services.embedding import embedding_service
from app.services.retrieval import RetrievalService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_risk(body: AnalysisRequestBody, db: AsyncSession = Depends(get_db)):
    text_query = body.request.text

    # 1. Get embedding for the query
    try:
        query_embedding = await embedding_service.get_embeddings(text_query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding error: {str(e)}")

    # 2. Perform hybrid retrieval
    retriever = RetrievalService(db)

    # Parallelize these if possible, but for MVP sequential is fine
    bm25_cases = await retriever.search_cases_bm25(text_query)
    vector_cases = await retriever.search_cases_vector(query_embedding)

    # 3. RRF Fusion
    fused_results = retriever.rrf_fusion(bm25_cases, vector_cases)

    if not fused_results:
        # If no cases found, just return a prompt with whatever knowledge we have
        tips = await retriever.search_tips(text_query, query_embedding)
        return AnalysisResponse(
            result_type="RAG_Prompt",
            data=RAGPromptData(
                risk_level="LOW",
                rrf_score=0.0,
                prompt=f"分析用户请求: {text_query}",
                context=RAGPromptContext(
                    relevant_cases=[],
                    anti_fraud_tips=[{"title": t.title, "content": t.content} for t in tips],
                ),
            ),
        )

    top_result = fused_results[0]
    top_score = top_result["score"]

    # 4. Threshold Check
    if top_score >= settings.HIGH_RISK_THRESHOLD:
        matched_cases = []
        # Return top matches for Direct_Hit
        for res in fused_results[:3]:
            if res["score"] > 0.1:  # Some minimal relevance
                c = res["item"]
                matched_cases.append(
                    MatchedCase(
                        case_id=c.id,
                        description=c.description,
                        confidence=res["score"],
                        fraud_type=c.fraud_type,
                        key_indicators=c.keywords or [],
                    )
                )

        return AnalysisResponse(
            result_type="Direct_Hit",
            data=DirectHitData(risk_level="HIGH", matched_cases=matched_cases),
        )
    else:
        # RAG Prompt route
        tips = await retriever.search_tips(text_query, query_embedding)

        relevant_cases_data = []
        for res in fused_results[:3]:
            c = res["item"]
            relevant_cases_data.append({"description": c.description, "fraud_type": c.fraud_type})

        tips_data = [{"title": t.title, "content": t.content} for t in tips]

        # Build Prompt
        prompt = f"""你是一个专业的反诈骗助手。请根据以下案例信息和反诈知识，
分析用户遇到的情况是否属于诈骗，并给出专业的判断和建议。

【用户咨询】
{text_query}

【相关案例】
{chr(10).join([f"- {c['description']}" for c in relevant_cases_data])}

【反诈知识】
{chr(10).join([f"- {t['title']}: {t['content']}" for t in tips_data])}

请给出你的分析："""

        return AnalysisResponse(
            result_type="RAG_Prompt",
            data=RAGPromptData(
                risk_level="MEDIUM" if top_score > 0.5 else "LOW",
                rrf_score=top_score,
                prompt=prompt,
                context=RAGPromptContext(
                    relevant_cases=relevant_cases_data, anti_fraud_tips=tips_data
                ),
            ),
        )
