import json
from datetime import UTC, datetime
from typing import Any, Dict, List

import structlog
from llama_index.core import Document, PropertyGraphIndex, Settings
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel

from src.domain.intelligence.schema import AIOverview, NewsAnomaly

logger = structlog.get_logger()

class AIService:
    """
    Intelligence service powered by LlamaIndex and Ollama.
    Generates structured market overviews and detects anomalies.
    """

    def __init__(
        self, 
        base_url: str = "http://ollama:11434", 
        model: str = "qwen3.5:9b",
        timeout: float = 120.0
    ):
        self.llm = Ollama(
            model=model, 
            base_url=base_url, 
            request_timeout=timeout,
            json_mode=True
        )
        # Use as_structured_llm to enforce Pydantic output
        self.structured_llm = self.llm.as_structured_llm(AIOverview)
        
    async def generate_summary(self, context: Dict[str, Any]) -> AIOverview:
        """
        Generate a structured AI overview based on provided market and news context.
        """
        # Convert context to a readable string for the LLM
        news_titles = [f"- {n['title']} (Sentiment: {n['sentiment']:.2f}, Impact: {n['impact']:.2f})" for n in context.get("news", [])]
        news_str = "\n".join(news_titles) if news_titles else "No recent news."
        
        risk = context.get("risk", {})
        macro = context.get("macro", {})
        
        prompt = f"""
Analyze the following market context and provide a premium, insightful summary.

### Market Risk & Performance
- Realized PnL: {risk.get('realized_pnl', 0.0):.2f}
- Win Rate: {risk.get('win_rate', 0.0):.1%}
- Trades Today: {risk.get('trades_count', 0)}
- Drawdown: {risk.get('drawdown', 0.0):.1%}
- Circuit Breaker: {'ACTIVE' if risk.get('circuit_breaker_active') else 'INACTIVE'}

### Macro Sentiment
- Fear & Greed Index: {macro.get('fear_and_greed', 50)}

### Recent News Events
{news_str}

### Instructions
1. Write a professional, concise narrative summary (2-3 paragraphs) of the current state.
2. Determine the overall market sentiment (Bullish, Bearish, or Neutral).
3. Assign a sentiment score from -1.0 to 1.0.
4. Assign a risk score from 0.0 (safe) to 1.0 (extremely risky).
5. Identify any specific anomalies or critical news events as NewsAnomaly objects.
6. Return the data in the AIOverview JSON format.
"""
        try:
            # chat with structured LLM
            from llama_index.core.llms import ChatMessage
            
            response = await self.structured_llm.achat([
                ChatMessage(role="system", content="You are the OmniTrader Intelligence Core, a senior market analyst AI."),
                ChatMessage(role="user", content=prompt)
            ])
            
            # The structured LLM returns a response where the message content is already parsed or in JSON
            # In LlamaIndex 0.12+, as_structured_llm might return the pydantic object directly in message.content 
            # if it used a tool or just a JSON string.
            
            content = response.message.content
            if isinstance(content, str):
                try:
                    data = json.loads(content)
                    # Add current timestamp if missing
                    if "timestamp" not in data:
                        data["timestamp"] = int(datetime.now(UTC).timestamp())
                    return AIOverview(**data)
                except json.JSONDecodeError:
                    logger.error("ai_service_json_decode_error", content=content)
                    raise
            elif isinstance(content, dict):
                if "timestamp" not in content:
                    content["timestamp"] = int(datetime.now(UTC).timestamp())
                return AIOverview(**content)
            elif isinstance(content, AIOverview):
                return content
            else:
                logger.error("ai_service_unexpected_response_type", type=str(type(content)))
                raise ValueError("Unexpected response type from LLM")
                
        except Exception as e:
            logger.error("ai_service_generation_failed", error=str(e))
            # Fallback
            return AIOverview(
                narrative="Intelligence generation failed due to an internal error.",
                sentiment="Neutral",
                sentiment_score=0.0,
                risk_score=0.5,
                anomalies=[],
                timestamp=int(datetime.now(UTC).timestamp())
            )

    async def save_overview(self, overview: AIOverview, db: Any, redis_client: Any):
        """Save the generated overview to Redis and Memgraph."""
        try:
            # Save to Redis for fast frontend access
            redis_client.set("ai:overview:latest", overview.model_dump_json())
            
            # Save to Memgraph for history and relationships
            query = """
            CREATE (o:AIOverview {
                narrative: $narrative,
                sentiment: $sentiment,
                sentiment_score: $sentiment_score,
                risk_score: $risk_score,
                timestamp: $timestamp
            })
            WITH o
            UNWIND $anomalies AS anomaly
            CREATE (a:NewsAnomaly {
                title: anomaly.title,
                description: anomaly.description,
                impact_score: anomaly.impact_score
            })
            CREATE (o)-[:HAS_ANOMALY]->(a)
            """
            
            async with db._driver.session() as session:
                await session.run(
                    query,
                    narrative=overview.narrative,
                    sentiment=overview.sentiment,
                    sentiment_score=overview.sentiment_score,
                    risk_score=overview.risk_score,
                    timestamp=overview.timestamp,
                    anomalies=[a.model_dump() for a in overview.anomalies]
                )
            logger.info("ai_overview_saved", timestamp=overview.timestamp)
        except Exception as e:
            logger.error("ai_overview_save_failed", error=str(e))
