import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Case, Tip
from app.db.session import get_db
from app.schemas.data import CaseCreateRequest, TipCreateRequest
from app.services.embedding import embedding_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/case")
async def inject_case(body: CaseCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Get embedding for case description
        embedding = await embedding_service.get_embeddings(body.case.description)

        new_case = Case(
            description=body.case.description,
            fraud_type=body.case.fraud_type,
            amount=body.case.amount,
            keywords=body.case.keywords,
            embedding=embedding,
        )

        db.add(new_case)
        await db.commit()
        await db.refresh(new_case)

        return {"status": "success", "message": "案例注入成功", "case_id": str(new_case.id)}
    except Exception as e:
        logger.error(f"Error injecting case: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tip")
async def inject_tip(body: TipCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Get embedding for tip content (combined title and content)
        combined_text = f"{body.tip.title} {body.tip.content}"
        embedding = await embedding_service.get_embeddings(combined_text)

        new_tip = Tip(
            title=body.tip.title,
            content=body.tip.content,
            category=body.tip.category,
            keywords=body.tip.keywords,
            embedding=embedding,
        )

        db.add(new_tip)
        await db.commit()
        await db.refresh(new_tip)

        return {"status": "success", "message": "知识注入成功", "tip_id": str(new_tip.id)}
    except Exception as e:
        logger.error(f"Error injecting tip: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
