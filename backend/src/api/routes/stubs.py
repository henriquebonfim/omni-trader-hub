"""
Placeholder endpoints returning 501 Not Implemented for unimplemented features.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["stubs"])

def stub_response(task: str):
    return JSONResponse(status_code=501, content={"error": "Not implemented", "task": task})

@router.get("/bots")
async def get_bots():
    return stub_response("T37")

@router.post("/bots")
async def create_bot():
    return stub_response("T37")

@router.get("/bots/{bot_id}")
async def get_bot(bot_id: str):
    return stub_response("T37")

@router.put("/bots/{bot_id}")
async def update_bot(bot_id: str):
    return stub_response("T37")

@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: str):
    return stub_response("T37")

@router.post("/bots/{bot_id}/trade/open")
async def open_trade(bot_id: str):
    return stub_response("T37")

@router.post("/bots/{bot_id}/trade/close")
async def close_trade(bot_id: str):
    return stub_response("T37")

@router.get("/graph/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    return stub_response("T33")

@router.get("/graph/crisis")
async def get_crisis():
    return stub_response("T34")

@router.put("/graph/crisis")
async def toggle_crisis():
    return stub_response("T34")

@router.get("/graph/news")
async def get_news():
    return stub_response("T33")

@router.post("/backtest/run")
async def run_backtest():
    return stub_response("T35")

@router.get("/backtest/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    return stub_response("T35")

@router.get("/backtest/history")
async def get_backtest_history():
    return stub_response("T35")

@router.get("/markets")
async def get_markets():
    return stub_response("T42")

@router.get("/env")
async def get_env():
    return stub_response("T41")

@router.put("/env")
async def update_env():
    return stub_response("T41")

@router.post("/system/restart")
async def restart_system():
    return stub_response("T41")
