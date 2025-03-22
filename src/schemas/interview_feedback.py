from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class HeaderObject:
    title: str = "Interview Feedback"
    position: Dict[str, int] = field(default_factory=lambda: {"x": 200,"y": 50})
    font: Dict[str,Any] = field(default_factory=lambda:{"name": "Helvetica-Bold", "size": 16})

@dataclass
class CandidateDetailItem:
    label:str
    value:str

@dataclass
class ScoreDistribution:
    criterion: str
    score: float

@dataclass 
class EvaluationSummaryObject:
    question_number: int
    question: str
    evaluation_summary: Dict[str, Dict[str, str]]
    code_snippet: str
    question_score: int
    criteria_scores: List[float]

@dataclass
class OverallRecommendation:
    title: str
    content: str

@dataclass
class InterviewFeedbackData:
    header: HeaderObject
    candidate_details:List[CandidateDetailItem]
    evaluation_summary: List[EvaluationSummaryObject]
    overall_recommendation: List[OverallRecommendation]
    