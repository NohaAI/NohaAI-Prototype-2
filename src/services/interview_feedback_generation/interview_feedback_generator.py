from src.services.interview_feedback_generation.feedback_data_preparation import prepare_interview_feedback_data
from src.schemas.interview_feedback import PDFLayout, PDFSpacingConfig, PDFStyleConfig, InterviewFeedbackDataObject
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
from src.services.interview_feedback_generation.interview_feedback_pdf_layout import get_interview_feedback_pdf_layout

def build_header_section(layout: PDFLayout, header_data):
    """Build content for the header section"""
    content = []
    content.append(Paragraph(header_data.title, layout.styles.title_style))
    content.append(Spacer(1, layout.spacing.alter_title))
    return content

def build_candidate_details_section(layout: PDFLayout, candidate_details):
    """Build content for candidate details section"""
    content = []
    for detail in candidate_details:
        content.append(Paragraph(f"<b>{detail.label}:</b>" + f"{detail.value}", layout.styles.normal_style))
        content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    content.append(Spacer(1, layout.spacing.alter_section))
    return content

def build_evaluation_summary_section(layout: PDFLayout, evaluation_summary_object):
    """Build content for a single evaluation"""
    content = []
    
    # Add page break before each question (except the first)
    if evaluation_summary_object.question_number > 1:
        content.append(PageBreak())
    
    # Question header
    content.append(Paragraph(f"QUESTION {evaluation_summary_object.question_number}:", layout.styles.heading_style))
    content.append(Paragraph(evaluation_summary_object.question, layout.styles.normal_style))
    content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Evaluation summary
    content.append(Paragraph("EVALUATION SUMMARY:", layout.styles.heading_style))
    criteria_list = []
    for criterion, details in evaluation_summary_object.evaluation_summary['evaluation_summary'].items():
        content.append(Paragraph(f"<b>{criterion} </b>", layout.styles.normal_style))
        criteria_list.append(criterion)
        content.append(Paragraph(f"<b>Summary:</b> {details['Summary']}", layout.styles.normal_style))
        content.append(Paragraph(f"<b>Strengths:</b> {details['Strengths']}", layout.styles.normal_style))
        content.append(Paragraph(f"<b>Weaknesses:</b> {details['Weaknesses']}", layout.styles.normal_style))
        content.append(Paragraph(f"<b>Judgment:</b> {details['Judgment']}", layout.styles.normal_style))
        content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Code snippet
    content.append(Paragraph("CANDIDATE'S CODE ATTEMPT:", layout.styles.heading_style))
    # Format code with preserved whitespace and line breaks
    code_text = evaluation_summary_object.code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;')
    content.append(Paragraph(code_text, layout.styles.code_style))
    content.append(Spacer(1, layout.spacing.alter_code))
    
    # Score
    content.append(Paragraph("SCORE:", layout.styles.heading_style))
    content.append(Paragraph(f"{evaluation_summary_object.question_score}/10", layout.styles.normal_style))
    content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Score distribution
    content.append(Paragraph("SCORE DISTRIBUTION:", layout.styles.heading_style))
    
    for i, score in enumerate(evaluation_summary_object.criteria_scores):
        if i < len(criteria_list):  # Make sure we don't exceed the criteria_list list
            content.append(Paragraph(
                f"{criteria_list[i]}: {score}/10", 
                layout.styles.normal_style
            ))
    
    content.append(Spacer(1, layout.spacing.alter_section))
    return content

def build_recommendation_section(layout: PDFLayout, recommendation):
    """Build content for recommendation section"""
    content = []
    content.append(PageBreak())  # Force page break
    content.append(Paragraph(recommendation.title, layout.styles.heading_style))
    content.append(Paragraph(recommendation.content, layout.styles.normal_style))
    return content

def generate_interview_feedback_report(session_state, chat_history, assessment_payloads, code_snippet=None):
    # Prepare interview feedback data
    interview_feedback_data_object = prepare_interview_feedback_data(
        session_state, chat_history, assessment_payloads, code_snippet
    )

    # Prepare PDF layout
    layout = get_interview_feedback_pdf_layout()
    interview_feedback_pdf_output_path="interview_feedback.pdf"
    # Create document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=layout.page_size,
        leftMargin=layout.margin,
        rightMargin=layout.margin,
        topMargin=layout.margin,
        bottomMargin=layout.margin
    )
    
    # Build content
    content = []
    content.extend(build_header_section(layout, interview_feedback_data_object.header))
    content.extend(build_candidate_details_section(layout, interview_feedback_data_object.candidate_details))
    
    for evaluation_summary_object in interview_feedback_data_object.evaluation_summary_object_list:
        content.extend(build_evaluation_summary_section(layout, evaluation_summary_object))
    
    content.extend(build_recommendation_section(layout, interview_feedback_data_object.overall_recommendation))
    
    # Generate and save PDF
    doc.build(content)
    buffer.seek(0)
    
    if interview_feedback_pdf_output_path:
        with open(interview_feedback_pdf_output_path, "wb") as f:
            f.write(buffer.getvalue())
    return buffer