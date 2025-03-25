from dataclasses import dataclass, field
from typing import List, Dict, Any
from reportlab.lib.styles import ParagraphStyle
from dataclasses import dataclass, field
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter

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
     
class EmptyChatHistoryException(Exception):
    def __init__(self, message="Chat history can not be empty", chat_history=None):
        self.message = message
        self.chat_history = chat_history
        
        # Enhance message if list name is provided
        if chat_history:
            self.message += f" (list: {chat_history})"
        
        super().__init__(self.message)

class EmptyAssessmentPayloadException(Exception):
    def __init__(self, message="Assessment payload can not be empty", assessment_payloads=None):
        self.message = message
        self.assessment_payloads = assessment_payloads
        
        # Enhance message if list name is provided
        if assessment_payloads:
            self.message += f" (list: {assessment_payloads})"
        
        super().__init__(self.message)