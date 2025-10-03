from pydantic import BaseModel
from typing import List

class EnvironmentalQuality(BaseModel):
    """Đánh giá chất lượng môi trường bằng AI"""
    overall_rating: str  # excellent, good, moderate, poor, hazardous
    score: float  # 0-100
    health_risk: str  # low, moderate, high, very_high
    summary: str  # Tóm tắt tình hình
    recommendations: List[str]  # Khuyến nghị
    concerns: List[str]  # Mối lo ngại
    ai_reasoning: str  # Lý do AI đưa ra đánh giá này