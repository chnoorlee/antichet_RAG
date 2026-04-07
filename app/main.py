from fastapi import Depends, FastAPI, Header, HTTPException

from app.api.v1.analyze import router as analyze_router
from app.api.v1.data import router as data_router
from app.core.config import settings

app = FastAPI(title="Anti-Fraud RAG System", version="0.1.0")


# Simple API Key authentication middleware
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


# Health check endpoint (no auth)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers with auth
app.include_router(
    analyze_router, prefix="/api/v1", tags=["Analysis"], dependencies=[Depends(verify_api_key)]
)
app.include_router(
    data_router,
    prefix="/api/v1/data",
    tags=["Data Injection"],
    dependencies=[Depends(verify_api_key)],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
