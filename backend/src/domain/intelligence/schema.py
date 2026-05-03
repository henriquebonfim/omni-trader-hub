from typing import List, Optional
from pydantic import BaseModel, Field

class NewsAnomaly(BaseModel):
    title: str
    description: str
    impact_score: float

class AIOverview(BaseModel):
    narrative: str = Field(..., description="High-level narrative summary of the market")
    sentiment: str = Field(..., description="Overall market sentiment (Bullish, Bearish, Neutral)")
    sentiment_score: float = Field(..., description="Sentiment score from -1.0 to 1.0")
    risk_score: float = Field(..., description="Current risk score from 0.0 to 1.0")
    anomalies: List[NewsAnomaly] = Field(default_factory=list, description="List of detected anomalies or critical news")
    timestamp: int = Field(..., description="Unix timestamp of generation")
