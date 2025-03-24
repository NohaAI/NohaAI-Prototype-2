from src.services.interview_feedback_generation.feedback_data_preparation import prepare_interview_feedback_data
from src.schemas.interview_feedback import PDFLayout
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
import io
from src.services.interview_feedback_generation.interview_feedback_pdf_layout import get_interview_feedback_pdf_layout

def build_header_section(layout: PDFLayout, header_data):
    """Build content for the header section"""
    header_content = []
    header_content.append(Paragraph(header_data.title, layout.styles.title_style))
    header_content.append(Spacer(1, layout.spacing.alter_title))
    return header_content

def build_candidate_details_section(layout: PDFLayout, candidate_details):
    """Build content for candidate details section"""
    candidate_details_content = []
    for detail in candidate_details:
        candidate_details_content.append(Paragraph(f"<b>{detail.label}:</b>" + f"{detail.value}", layout.styles.normal_style))
        candidate_details_content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    candidate_details_content.append(Spacer(1, layout.spacing.alter_section))
    return candidate_details_content

def build_evaluation_summary_section(layout: PDFLayout, evaluation_summary_object):
    """Build content for a single evaluation"""
    evaluation_summary_content = []
    
    # Add page break before each question (except the first)
    if evaluation_summary_object.question_number > 1:
        evaluation_summary_content.append(PageBreak())
    
    # Question header
    evaluation_summary_content.append(Paragraph(f"QUESTION {evaluation_summary_object.question_number}:", layout.styles.heading_style))
    evaluation_summary_content.append(Paragraph(evaluation_summary_object.question, layout.styles.normal_style))
    evaluation_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Evaluation summary
    evaluation_summary_content.append(Paragraph("EVALUATION SUMMARY:", layout.styles.heading_style))
    criteria_list = []
    for criterion, details in evaluation_summary_object.evaluation_summary['evaluation_summary'].items():
        evaluation_summary_content.append(Paragraph(f"<b>{criterion} </b>", layout.styles.normal_style))
        criteria_list.append(criterion)
        evaluation_summary_content.append(Paragraph(f"<b>Summary:</b> {details['Summary']}", layout.styles.normal_style))
        evaluation_summary_content.append(Paragraph(f"<b>Strengths:</b> {details['Strengths']}", layout.styles.normal_style))
        evaluation_summary_content.append(Paragraph(f"<b>Weaknesses:</b> {details['Weaknesses']}", layout.styles.normal_style))
        evaluation_summary_content.append(Paragraph(f"<b>Judgment:</b> {details['Judgment']}", layout.styles.normal_style))
        evaluation_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Code snippet
    evaluation_summary_content.append(Paragraph("CANDIDATE'S CODE ATTEMPT:", layout.styles.heading_style))
    # Format code with preserved whitespace and line breaks
    code_text = evaluation_summary_object.code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;')
    evaluation_summary_content.append(Paragraph(code_text, layout.styles.code_style))
    evaluation_summary_content.append(Spacer(1, layout.spacing.alter_code))
    
    # Score
    evaluation_summary_content.append(Paragraph("SCORE:", layout.styles.heading_style))
    evaluation_summary_content.append(Paragraph(f"{evaluation_summary_object.question_score}/10", layout.styles.normal_style))
    evaluation_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    # Score distribution
    evaluation_summary_content.append(Paragraph("SCORE DISTRIBUTION:", layout.styles.heading_style))
    
    for i, score in enumerate(evaluation_summary_object.criteria_scores):
        if i < len(criteria_list):  # Make sure we don't exceed the criteria_list list
            evaluation_summary_content.append(Paragraph(
                f"<b>{criteria_list[i]}:</b> {score}/10", 
                layout.styles.normal_style
            ))
    
    evaluation_summary_content.append(Spacer(1, layout.spacing.alter_section))
    return evaluation_summary_content

def build_recommendation_section(layout: PDFLayout, recommendation):
    """Build content for recommendation section"""
    recommendation_content = []
    recommendation_content.append(PageBreak())  # Force page break
    recommendation_content.append(Paragraph(recommendation.title, layout.styles.heading_style))
    recommendation_content.append(Paragraph(recommendation.content, layout.styles.normal_style))
    return recommendation_content

def generate_interview_feedback_report(session_state, chat_history, assessment_payloads, code_snippet=None):
    # Prepare interview feedback data
    interview_feedback_data_object = prepare_interview_feedback_data(
        session_state, chat_history, assessment_payloads, code_snippet
    )

    # Prepare PDF layout
    layout = get_interview_feedback_pdf_layout()
    interview_feedback_pdf_output_path="interview_feedback.pdf"
    # Create document
    buffer = io.BytesIO() #in memory binary stream
    doc = SimpleDocTemplate(
        buffer,
        pagesize=layout.page_size,
        leftMargin=layout.margin,
        rightMargin=layout.margin,
        topMargin=layout.margin,
        bottomMargin=layout.margin
    )
    
    # Build content
    interview_feedback_content = []
    interview_feedback_content.extend(build_header_section(layout, interview_feedback_data_object.header_object))
    interview_feedback_content.extend(build_candidate_details_section(layout, interview_feedback_data_object.candidate_details_object))
    
    for evaluation_summary_object in interview_feedback_data_object.evaluation_summary_object_list:
        interview_feedback_content.extend(build_evaluation_summary_section(layout, evaluation_summary_object))
    
    interview_feedback_content.extend(build_recommendation_section(layout, interview_feedback_data_object.overall_recommendation_object))
    
    # Generate and save PDF
    doc.build(interview_feedback_content)
    buffer.seek(0) #resets the pointer to buffer at the start for parsing
    
    if interview_feedback_pdf_output_path:
        with open(interview_feedback_pdf_output_path, "wb") as f:
            f.write(buffer.getvalue())
    return buffer