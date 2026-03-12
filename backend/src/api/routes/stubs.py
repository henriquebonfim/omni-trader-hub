"""
Placeholder endpoints returning 501 Not Implemented for unimplemented features.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["stubs"])


def stub_response(task: str):
    return JSONResponse(
        status_code=501, content={"error": "Not implemented", "task": task}
    )


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


@router.post("/backtest/run")
async def run_backtest():
    return stub_response("T35")


@router.get("/backtest/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    return stub_response("T35")


@router.get("/backtest/history")
async def get_backtest_history():
    return stub_response("T35")


# NOTE: /markets, /env, /system/restart are real routes (T41/T42) — no stubs needed.
