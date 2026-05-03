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


@router.post("/backtest/run")
async def run_backtest():
    return stub_response("T35")


@router.get("/backtest/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    return stub_response("T35")


@router.get("/backtest/history")
async def get_backtest_history():
    return stub_response("T35")
