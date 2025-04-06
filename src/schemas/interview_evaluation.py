from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from reportlab.lib.styles import ParagraphStyle
from dataclasses import dataclass, field
from reportlab.lib.pagesizes import letter

#DATA CLASSES FOR INTERVIEW EVALUATION DATA PREPARATION
@dataclass
class HeaderObject:
    
    """Represents the title and styling configuration for the interview evaluation header."""
    
    title: str = "Interview Evaluation"  # The main title of the interview evaluation document.
    position: Dict[str, int] = field(default_factory=lambda: {"x": 200, "y": 50})  # Position coordinates of the title.
    font: Dict[str, Any] = field(default_factory=lambda: {"name": "Helvetica-Bold", "size": 16})  # Font style for the title.

#CandidateDetailItem is an item in candidate_detail_item_list
@dataclass
class CandidateDetailItem:
    
    """Represents a specific candidate detail as a labeled key-value pair."""
    
    label: str  # The name of the candidate detail (e.g., "Candidate Name", "Interview ID").
    value: str  # The corresponding value for the detail (e.g., actual candidate name, interview ID).

#TODO: check how this can be used instead of CandidateDetailsItem
@dataclass
class TestCandidateDetailsObject:
    
    """Holds essential candidate and interview metadata, including name, ID, date, bot name, and scores."""
    
    candidate_name: str  # Name of the candidate.
    interview_id: int  # Unique identifier for the interview.
    date: str  # Date when the interview took place.
    bot_name: str  # Name of the bot conducting the interview.
    overall_score: int  # Candidate's total score obtained.
    total_possible_score: int  # Maximum possible score.

@dataclass 
class EvaluationSummaryObject:
    
    """Represents the evaluation details for a specific question, including summaries, scores, and code snippet."""
    
    question_number: int  # The number of the question in the interview.
    question: str  # The actual question asked.
    evaluation_summary: Union[str, Dict[str, Dict[str, str]]]  # Detailed evaluation including summary, strengths, weaknesses, and judgment.
    question_score: int  # Score awarded for this question.
    criteria_scores: List[float]  # Scores for individual evaluation criteria.

@dataclass
class AppendixObject:
    code_snippet: List[str]  # The candidate's code solution for the question.
    chat_history: List[Dict]
    video_url : str

@dataclass
class OverallRecommendationObject:
   
    """Represents the final hiring recommendation, including a title and a detailed assessment of the candidate's performance."""
   
    title: str  # The section header (e.g., "OVERALL RECOMMENDATION").
    content: Union[str,None]  # The final recommendation based on the candidate's evaluation.

@dataclass
class InterviewEvaluationDataObject:
   
    """Encapsulates the complete interview evaluation, including header, candidate details, evaluation summaries, and recommendations."""
   
    header_object: HeaderObject
    candidate_details_object: List[CandidateDetailItem]
    evaluation_summary_object_list: List[EvaluationSummaryObject]
    overall_recommendation_object: List[OverallRecommendationObject]
    appendix_object: AppendixObject
#DATA CLASSES FOR PDF LAYOUT

@dataclass
class PDFStyleConfig:
   
    """Defines the text styling for different elements in the PDF report."""
   
    title_style: ParagraphStyle  # Style for the main title of the report.
    heading_style: ParagraphStyle  # Style for section headings.
    normal_style: ParagraphStyle  # Style for regular body text.
    code_style: ParagraphStyle  # Style for code snippets in the report.

@dataclass
class PDFSpacingConfig:
   
    """Specifies spacing adjustments for different sections in the PDF layout."""
   
    alter_title: int = 30  # Space after the title section.
    alter_section: int = 20  # Space between major sections.
    alter_paragraph: int = 10  # Space between paragraphs.
    alter_code: int = 15  # Space before and after code snippets.

@dataclass
class PDFLayout:
   
    """Defines the overall PDF layout, including page size, margins, spacing, and styles."""
   
    page_size: tuple = letter  # The page dimensions (default: letter size).
    margin: int = 50  # Margin around the content.
    line_height: int = 15  # Default line spacing.
    styles: PDFStyleConfig = None  # Reference to text style configurations.
    spacing: PDFSpacingConfig = None  # Reference to spacing configurations.

@dataclass
class PDFLayoutTest:
    """
    Defines the overall PDF layout, including page size, margins, spacing, styles, and header configuration.
    
    Attributes:
        page_size (tuple): The page dimensions (default: letter size).
        margin (int): Margin around the content.
        line_height (int): Default line spacing.
        styles (PDFStyleConfig): Reference to text style configurations.
        spacing (PDFSpacingConfig): Reference to spacing configurations.
        header_func (Optional[Callable]): Function to create header for each page.
    """
    
    page_size: tuple = letter
    margin: int = 50
    line_height: int = 15
    styles: Optional['PDFStyleConfig'] = None
    spacing: Optional['PDFSpacingConfig'] = None
    header_func: Optional[Callable] = None
    
    def __post_init__(self):
        """
        Post-initialization validation to ensure critical attributes are set.
        """
        # Optional additional validation can be added here
        if self.styles is None:
            raise ValueError("PDFStyleConfig must be provided")
        if self.spacing is None:
            raise ValueError("PDFSpacingConfig must be provided")
    