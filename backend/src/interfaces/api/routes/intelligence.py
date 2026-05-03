from fastapi import APIRouter, Depends, HTTPException, Request
import json
from typing import Dict, Any

from ..auth import verify_api_key
from src.infrastructure.database.redis import get_redis_client

router = APIRouter(tags=["intelligence"], dependencies=[Depends(verify_api_key)])

@router.get("/overview")
async def get_ai_overview(request: Request):
    """
    Fetch the latest AI-generated market overview.
    """
    redis_client = get_redis_client()
    overview_raw = redis_client.get("ai:overview:latest")
    
    if not overview_raw:
        return {
            "narrative": "AI Intelligence is currently gathering data. Please check back in a few minutes.",
            "sentiment": "Neutral",
            "sentiment_score": 0.0,
            "risk_score": 0.0,
            "anomalies": [],
            "timestamp": 0,
            "status": "pending"
        }
        
    try:
        data = json.loads(overview_raw)
        data["status"] = "ready"
        return data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to decode AI overview from storage.")

@router.post("/trigger")
async def trigger_ai_overview(request: Request):
    """
    Manually trigger the AI overview generation task.
    """
    from src.interfaces.workers.tasks import generate_ai_overview
    task = generate_ai_overview.delay()
    return {"status": "triggered", "task_id": task.id}
