from src.dao.interview import get_candidate_name
from src.config import constants as const
from datetime import datetime
from typing import List
from src.utils import helper
from src.services.workflows.evaluation_summary_generator import generate_evaluation_summary
from src.schemas.interview_feedback import HeaderObject, CandidateDetailItem, EvaluationSummaryObject, OverallRecommendationObject, InterviewFeedbackDataObject
from src.services.workflows.overall_recommendation_generator import generate_overall_recommendation
from src.dao.assessment import AssessmentDAO
from src.dao.chat_history import ChatHistoryDAO
from src.dao.user import get_candidate_interview_id

from src.schemas.interview_feedback import EmptyAssessmentPayloadException, EmptyChatHistoryException

def create_header_object() -> HeaderObject:
    
    return HeaderObject(
        title = "Interview Feedback",
        position = {"x": 200, "y": 50},
        font = {"name": "Helvetica-Bold", "size": 16}
    )

def create_candidate_details_object(interview_id, assessment_payloads) -> List[CandidateDetailItem]:
    
    candidate_name = get_candidate_name(interview_id)
    date = datetime.now().date()
    overall_score,total_possible_score = helper.calculate_overall_score(assessment_payloads)
    candidate_details_object = [
        CandidateDetailItem(label= "Candidate Name", value= candidate_name),
        CandidateDetailItem(label= "Interview ID", value= interview_id),
        CandidateDetailItem(label= "Date", value= date),
        CandidateDetailItem(label= "Interview Conducted By", value= const.BOT_NAME),
        CandidateDetailItem(label= "Overall Score", value= f"{overall_score}/{total_possible_score}")
    ]
    return candidate_details_object

def create_evaluation_summary_object_list(question_id_list, chat_history, assessment_payloads, criteria_list ,code_snippet) -> List[EvaluationSummaryObject]:
    evaluation_summary_object_list = []
    
    evaluation_summary_list = generate_evaluation_summary(question_id_list, chat_history, assessment_payloads, criteria_list)
    #preparing list of EvaluationSummaryObject
    for i, ((question, criteria_scores, question_score, evaluation_summary), code_snippet) in enumerate(zip(evaluation_summary_list, code_snippet)):
        evaluation_object = EvaluationSummaryObject(
            question_number = i+1,
            question = question,
            evaluation_summary = evaluation_summary,
            code_snippet = code_snippet,
            question_score = question_score,
            criteria_scores = criteria_scores
        )
        evaluation_summary_object_list.append(evaluation_object)
    return evaluation_summary_object_list

def create_overall_recommendation_object(evaluation_summary_object_list, criteria_list) -> OverallRecommendationObject:
    
    overall_recommendation = generate_overall_recommendation(evaluation_summary_object_list, criteria_list)

    return OverallRecommendationObject (
        title =  "OVERALL RECOMMENDATION:",
        content =  overall_recommendation
    )
    
# def prepare_interview_feedback_data(session_state, chat_history, assessment_payloads,code_snippet = None) -> InterviewFeedbackDataObject:
def prepare_interview_feedback_data(user_email, code_snippet) -> InterviewFeedbackDataObject:
        
    try:
        interview_id_list = get_candidate_interview_id(user_email) #returns a list of interview_ids 
        
        interview_id = interview_id_list[-1]
        
        chat_history_instance = ChatHistoryDAO()
        chat_history_object = chat_history_instance.get_chat_history(interview_id)
        assessment_payloads_object = AssessmentDAO.get_assessments(interview_id)
        
        chat_history = helper.convert_chat_history_object_to_dict(chat_history_object)
        assessment_payloads = helper.convert_assessment_payload_object_to_dict(assessment_payloads_object)
        if len(assessment_payloads) == 0:
            raise EmptyAssessmentPayloadException(assessment_payloads = assessment_payloads)
    
        if len(chat_history) == 0:
            raise EmptyChatHistoryException(chat_history= chat_history)
        
        question_id_list = []
        
        for assessment_record in assessment_payloads:
            question_id_list.append(assessment_record['question_id'])

        if not code_snippet or code_snippet == []:
            code_snippet = []
            for i in range(len(assessment_payloads)):
                code_snippet.append("NO CODE SNIPPET PROVIDED")
        criteria_list = helper.create_criteria_list(assessment_payloads) #helper func to get the list of criteria

        header_object = create_header_object()
        
        candidate_details_object = create_candidate_details_object(interview_id, assessment_payloads)
        
        evaluation_summary_object_list = create_evaluation_summary_object_list(question_id_list, chat_history, assessment_payloads, criteria_list,code_snippet)
        
        overall_recommendation_object = create_overall_recommendation_object(evaluation_summary_object_list, criteria_list) 
        
        return InterviewFeedbackDataObject( 
            header_object =  header_object, 
            candidate_details_object =  candidate_details_object,
            evaluation_summary_object_list =  evaluation_summary_object_list,
            overall_recommendation_object =  overall_recommendation_object,
        )
    except Exception as e:
        print(f"ERROR OCCERED WHILE PREPARING DATA USING DATABASE : {e}")
        raise e