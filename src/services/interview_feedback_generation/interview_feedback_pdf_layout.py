from src.services.interview_feedback_generation.feedback_data_preparation import prepare_interview_feedback_data
from src.schemas.interview_feedback import PDFLayout, PDFSpacingConfig, PDFStyleConfig
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
def get_interview_feedback_pdf_layout() -> PDFLayout:
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=5
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=10,
        leftIndent=10,
        rightIndent=10,
        backColor=colors.lightgrey
    )
    
    style_config = PDFStyleConfig(
        title_style=title_style,
        heading_style=heading_style,
        normal_style=normal_style,
        code_style=code_style
    )
    
    spacing_config = PDFSpacingConfig()
    
    return PDFLayout(
        styles=style_config,
        spacing=spacing_config
    )
