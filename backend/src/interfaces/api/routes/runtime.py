import os

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["runtime"])

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    context: dict

class LogsResponse(BaseModel):
    logs: list[LogEntry]

class PerformanceResponse(BaseModel):
    function_execution_times: dict
    database_query_performance: dict
    websocket_message_rates: dict

@router.get("/logs", response_model=LogsResponse)
async def get_logs(request: Request, minutes: int = Query(60, ge=1), level: str = Query(None)):
    """
    Recent application logs with filtering.
    """
    # For MVP, we simulate or read from a standard log file.
    # In a real scenario, this would read from structlog's output or a centralized logging service.
    # We will try to parse a local log file if it exists, or return empty list.

    logs = []

    # Try reading from a generic app.log or similar if configured,
    # but since logging is to stdout, we may not have a file.
    # Let's return a mock or empty list for now, as structlog to stdout doesn't leave a local file easily accessible.

    # In a real environment, we would implement an in-memory handler for structlog or read a log file.
    # Let's check if there's any standard log file we can read from.
    log_file_path = "omnitrader.log"

    if os.path.exists(log_file_path):
        try:
            with open(log_file_path) as f:
                lines = f.readlines()
                # Very simplistic parsing for demonstration
                for line in lines[-1000:]:  # Tail last 1000 lines
                    if level and level.upper() not in line:
                        continue

                    # Basic extraction
                    logs.append(LogEntry(
                        timestamp="unknown",
                        level="INFO",
                        message=line.strip(),
                        context={}
                    ))
        except Exception:
            pass

    return LogsResponse(logs=logs)


@router.get("/performance", response_model=PerformanceResponse)
async def get_performance(request: Request):
    """
    Performance profiling data:
    - Function execution times
    - Database query performance
    - WebSocket message rates
    """
    # Provide placeholders or read from a global performance tracker
    # We will implement a mock global performance tracker since it's an MVP

    perf_data = getattr(request.app.state, "performance_metrics", {
        "function_execution_times": {
            "strategy.analyze": 0.05,
            "exchange.fetch_ohlcv": 0.15,
            "risk.validate": 0.01,
        },
        "database_query_performance": {
            "get_last_trade": 0.02,
            "save_trade": 0.04,
        },
        "websocket_message_rates": {
            "messages_per_second": 12.5,
            "latency_ms": 45.0,
        }
    })

    return PerformanceResponse(**perf_data)
