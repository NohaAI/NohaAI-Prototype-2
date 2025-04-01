from src.services.interview_evaluation_generation import evaluation_data_preparation_from_dao
from src.services.interview_evaluation_generation import evaluation_data_preparation_from_session_state 
from reportlab.platypus import SimpleDocTemplate
import io
from src.services.interview_evaluation_generation.interview_evaluation_format import get_interview_evaluation_format
from src.services.interview_evaluation_generation.evaluation_report_format_expt import get_interview_evaluation_format_expt
from src.services.interview_evaluation_generation.evaluation_report_layout import build_candidate_details_section, build_evaluation_summary_section, build_header_section, build_recommendation_section
from datetime import datetime
from src.utils import helper

def prepare_interview_evaluation_filepath(interview_evaluation_data_object):
    interview_time = interview_evaluation_data_object.candidate_details_object[3].value
    interview_time_obj = datetime.strptime(interview_time, "%H:%M:%S").time()
    formatted_interview_time = interview_time_obj.strftime("%H%Mh")
    interview_evaluation_pdf_output_path = f"reports/{interview_evaluation_data_object.candidate_details_object[0].value}_{interview_evaluation_data_object.candidate_details_object[2].value}_{formatted_interview_time}_evaluation.pdf"
    return interview_evaluation_pdf_output_path

def create_evaluation_report_buffer(interview_evaluation_data_object):
    layout = get_interview_evaluation_format()
    # layout = get_interview_evaluation_format_expt()
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
    
    # Build content in the following sequence:
    interview_evaluation_content = []
    interview_evaluation_content.extend(build_header_section(layout, interview_evaluation_data_object.header_object))
    interview_evaluation_content.extend(build_candidate_details_section(layout, interview_evaluation_data_object.candidate_details_object))
    
    for evaluation_summary_object in interview_evaluation_data_object.evaluation_summary_object_list:
        interview_evaluation_content.extend(build_evaluation_summary_section(layout, evaluation_summary_object))
    if interview_evaluation_data_object.overall_recommendation_object.content != None:
        interview_evaluation_content.extend(build_recommendation_section(layout, interview_evaluation_data_object.overall_recommendation_object))
    
    # Generate and save PDF
    doc.build(interview_evaluation_content)
    buffer.seek(0) #resets the pointer to buffer at the start for parsing
    return buffer

def generate_evaluation_report_from_dao(user_email, code_snippet=None):
    # Prepare interview evaluation data
    interview_evaluation_data_object = evaluation_data_preparation_from_dao.prepare_interview_evaluation_data(
        user_email,
        code_snippet
    )
    buffer = create_evaluation_report_buffer(interview_evaluation_data_object)
    interview_evaluation_pdf_output_path = prepare_interview_evaluation_filepath(interview_evaluation_data_object)
    helper.write_to_pdf(buffer, interview_evaluation_pdf_output_path)

def generate_evaluation_report_from_session_state(session_state, chat_history, assessment_payloads, code_snippet=None):
    # Prepare interview evaluation data
    interview_evaluation_data_object = evaluation_data_preparation_from_session_state.prepare_interview_evaluation_data(
        session_state, chat_history, assessment_payloads, code_snippet
    )
    buffer = create_evaluation_report_buffer(interview_evaluation_data_object)
    interview_evaluation_pdf_output_path = prepare_interview_evaluation_filepath(interview_evaluation_data_object)
    helper.write_to_pdf(buffer, interview_evaluation_pdf_output_path)
