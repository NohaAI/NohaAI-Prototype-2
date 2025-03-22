from src.dao.interview import get_candidate_name, get_interview_metadata
from src.config import constants as const
from datetime import datetime
from src.utils import helper
from src.services.workflows import evaluation_summary_generator
def create_header_object():
    header_object = {
        "title": "Interview Feedback",
        "position": {"x": 200, "y": 50},
        "font": {"name": "Helvetica-Bold", "size": 16}
    }
    return header_object

def create_candidate_details_object(session_state, chat_history, assessment_payloads):
    
    interview_id = session_state['interview_id']
    candidate_name = get_candidate_name(interview_id)
    date = datetime.now()
    overall_score,total_possible_score = helper.calculate_overall_score(assessment_payloads)
    candidate_details_object = [
        {"label": "Candidate Name", "value": candidate_name},
        {"label": "Interview ID", "value": interview_id},
        {"label": "Date", "value": date},
        {"label": "Interview Conducted By", "value": const.BOT_NAME},
        {"label": "Overall Score", "value": f"{overall_score}/{total_possible_score}"}
    ]
    return candidate_details_object

def create_evaluation_summary_list_object(session_state, chat_history, assessment_payloads, code_snippet):
    evaluation_object_list = []
    criteria_list = helper.create_criteria_list(assessment_payloads) #helper func to get the list of criteria
    evaluation_summary_list = evaluation_summary_generator(session_state, chat_history, assessment_payloads)
    for i, ((question, evaluation_summary, question_score, criteria_scores), code_snippet) in enumerate(zip(evaluation_summary_list, code_snippet)):

    return evaluation_object_list

def create_overall_recommendation_object(overall_recommendation = ""):
    overall_recommendation_object ={
        "title": "OVERALL RECOMMENDATION:",
        "content": overall_recommendation
    }
    return overall_recommendation_object

def prepare_interview_feedback_data(session_state, chat_history, assessment_payload):
    header_object = create_header_object()
    candidate_details_object = create_candidate_details_object()
    evaluation_summary_list_object = create_evaluation_summary_list_object()
    overall_recommendation_object = create_overall_recommendation_object()
    overall_pdf_object = header_object + candidate_details_object + evaluation_summary_list_object + overall_recommendation_object
    return overall_pdf_object