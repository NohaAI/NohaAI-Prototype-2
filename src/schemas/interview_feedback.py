from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from reportlab.lib.styles import ParagraphStyle
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from textwrap import wrap
import io

#DATA CLASSES FOR INTERVIEW FEEDBACK DATA PREPARATION
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
class OverallRecommendationObject:
    title: str
    content: str

@dataclass
class InterviewFeedbackDataObject:
    header_object: HeaderObject
    candidate_details_object: List[CandidateDetailItem]
    evaluation_summary_object_list: List[EvaluationSummaryObject]
    overall_recommendation_object: List[OverallRecommendationObject]

#DATA CLASSES FOR PDF LAYOUT

@dataclass
class PDFStyleConfig:
    title_style: ParagraphStyle 
    heading_style: ParagraphStyle
    normal_style: ParagraphStyle
    code_style: ParagraphStyle

@dataclass
class PDFSpacingConfig:
    alter_title: int = 30
    alter_section: int = 20
    alter_paragraph: int = 10
    alter_code: int = 15

@dataclass
class PDFLayout:
    """Class representing the PDF layout configuration"""
    page_size: tuple = letter
    margin: int = 50
    line_height: int = 15
    styles: PDFStyleConfig = None
    spacing: PDFSpacingConfig = None
     