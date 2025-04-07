
from src.schemas.interview_evaluation import PDFLayout
from reportlab.platypus import Paragraph, Spacer, PageBreak

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
        candidate_details_content.append(Paragraph(f"<b>{detail.label}:</b> " + f"{detail.value}", layout.styles.normal_style))
        candidate_details_content.append(Spacer(1, layout.spacing.alter_paragraph))
    candidate_details_content.append(Spacer(1, layout.spacing.alter_section))
    return candidate_details_content

def build_interview_summary_section(layout: PDFLayout, interview_summary_object):
    """Build content for interview summary section"""
    interview_summary_content = []
    interview_summary_content.append(Paragraph(interview_summary_object.title, layout.styles.heading_style))
    interview_summary_content.append(Paragraph(interview_summary_object.content, layout.styles.normal_style))
    interview_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
    interview_summary_content.append(Paragraph("The questions asked and the highlights of the answers provided are summarized below", layout.styles.normal_style))
    interview_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
    return interview_summary_content

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
    if evaluation_summary_object.question_score == 0:
        evaluation_summary_content.append(Paragraph(f"{evaluation_summary_object.evaluation_summary}", layout.styles.normal_style))
    else:
        evaluation_summary_content.append(Paragraph(evaluation_summary_object.evaluation_summary['evaluation_summary']['summary'], layout.styles.normal_style))
        evaluation_summary_content.append(Spacer(1, layout.spacing.alter_code))
        evaluation_summary_content.append(Paragraph(evaluation_summary_object.evaluation_summary['evaluation_summary']['strengths_weakness'], layout.styles.normal_style))
    # Code snippet
        # evaluation_summary_content.append(Paragraph("CANDIDATE'S CODE ATTEMPT:", layout.styles.heading_style))
        # # Format code with preserved whitespace and line breaks
        # code_text = evaluation_summary_object.code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;')
        # evaluation_summary_content.append(Paragraph(code_text, layout.styles.code_style))
        # evaluation_summary_content.append(Spacer(1, layout.spacing.alter_code))
        
        # COMMENTED UNTIL SCORE DISTRIBUTION IS COHERENT    
        # # Score
        # evaluation_summary_content.append(Paragraph("SCORE:", layout.styles.heading_style))
        # evaluation_summary_content.append(Paragraph(f"{evaluation_summary_object.question_score}/10", layout.styles.normal_style))
        # evaluation_summary_content.append(Spacer(1, layout.spacing.alter_paragraph))
        
        # # Score distribution
        # evaluation_summary_content.append(Paragraph("SCORE DISTRIBUTION:", layout.styles.heading_style))
        
        # for i, score in enumerate(evaluation_summary_object.criteria_scores):
        #     if i <b len(criteria_list):  # Make sure we don't exceed the criteria_list list
        #         evaluation_summary_content.append(Paragraph(
        #             f"<b>{criteria_list[i]}:</b> {score}/10", 
        #             layout.styles.normal_style
        #         ))
    
    evaluation_summary_content.append(Spacer(1, layout.spacing.alter_section))
    return evaluation_summary_content

def build_recommendation_section(layout: PDFLayout, overall_recommendation):
    """Build content for overall_recommendation section"""
    overall_recommendation_content = []
    overall_recommendation_content.append(PageBreak())  # Force page break
    overall_recommendation_content.append(Paragraph(overall_recommendation.title, layout.styles.heading_style))
    overall_recommendation_content.append(Paragraph(overall_recommendation.content, layout.styles.normal_style))
    return overall_recommendation_content

def build_appendix_section(layout: PDFLayout, appendix_object):
    appendix_content = [] 
    appendix_content.append(Paragraph("APPENDIX:", layout.styles.heading_style))
    appendix_content.append(Paragraph(f"<b>CHAT HISTORY:</b>", layout.styles.normal_style))
    for chat_history_record in appendix_object.chat_history:
        for key in chat_history_record.keys():
            appendix_content.append(Paragraph(f"<b>{key}:</b> {chat_history_record[key]}", layout.styles.normal_style))
        appendix_content.append(Spacer(1, layout.spacing.alter_paragraph))
    appendix_content.append(Spacer(1, layout.spacing.alter_paragraph))
    
    if appendix_object.code_snippet is not None: 
        appendix_content.append(Paragraph("<b>CODE SNIPPET:</b>", layout.styles.normal_style))
        for code_snippet in appendix_object.code_snippet:
            appendix_content.append(Paragraph(code_snippet, layout.styles.normal_style))
            # Format code with preserved whitespace and line breaks
            code_text = code_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;')
            appendix_content.append(Paragraph(code_text, layout.styles.code_style))
            appendix_content.append(Spacer(1, layout.spacing.alter_code))
        
    
    appendix_content.append(Spacer(1, layout.spacing.alter_paragraph))
    appendix_content.append(Paragraph(f"<b>VIDEO URL:</b> {appendix_object.video_url}", layout.styles.normal_style))
    # appendix_content.append(Paragraph(appendix_object.video_url, layout.styles.normal_style))
    
    return appendix_content