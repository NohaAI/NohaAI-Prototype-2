from src.dao.interview import get_candidate_name, get_interview_metadata
from src.config import constants as const
from datetime import datetime
from typing import List
from src.utils import helper
from src.services.workflows.evaluation_summary_generator import generate_evaluation_summary
from src.schemas.interview_feedback import HeaderObject, CandidateDetailItem, ScoreDistribution, EvaluationSummaryObject, OverallRecommendationObject, InterviewFeedbackDataObject
#TODO: check whether dataclasses can be used for this purpose
def create_header_object() -> HeaderObject:
    
    return HeaderObject(
        title = "Interview Feedback",
        position = {"x": 200, "y": 50},
        font = {"name": "Helvetica-Bold", "size": 16}
    )

def create_candidate_details_object(session_state, assessment_payloads) -> List[CandidateDetailItem]:
    
    interview_id = session_state['interview_id']
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

def create_evaluation_summary_list_object(session_state, chat_history, assessment_payloads, code_snippet) -> List[EvaluationSummaryObject]:
    evaluation_object_list = []
    criteria_list = helper.create_criteria_list(assessment_payloads) #helper func to get the list of criteria
    evaluation_summary_list = generate_evaluation_summary(session_state, chat_history, assessment_payloads, criteria_list)
    for i, ((question, criteria_scores, question_score, evaluation_summary), code_snippet) in enumerate(zip(evaluation_summary_list, code_snippet)):
        evaluation_object = EvaluationSummaryObject(
            question_number = i+1,
            question = question,
            evaluation_summary = evaluation_summary,
            code_snippet = code_snippet,
            question_score = question_score,
            criteria_scores = criteria_scores
        )
        evaluation_object_list.append(evaluation_object)
    return evaluation_object_list

def create_overall_recommendation_object(overall_recommendation) -> OverallRecommendationObject:
    return OverallRecommendationObject (
        title =  "OVERALL RECOMMENDATION:",
        content =  overall_recommendation
    )
    
def prepare_interview_feedback_data(session_state, chat_history, assessment_payloads,code_snippet = None) -> InterviewFeedbackDataObject:
    if not code_snippet or code_snippet == []:
        code_snippet = []
        for i in range(len(assessment_payloads)):
            code_snippet.append("NO CODE SNIPPET PROVIDED")
    header_object = create_header_object()
    print(f"HEADER OBJECT : \n {header_object} \n")
    candidate_details_object = create_candidate_details_object(session_state, assessment_payloads)
    print(f"CANDIDATE DETAILS OBJECT : \n  {candidate_details_object} \n")
    evaluation_summary_list_object = create_evaluation_summary_list_object(session_state, chat_history, assessment_payloads, code_snippet)
    print(f"EVALUATION SUMMARY LIST OBJECT : \n  {evaluation_summary_list_object} \n")
    overall_recommendation_object = create_overall_recommendation_object(overall_recommendation = "") #AT THE MOMENT THERE IS NO FUNC FOR GENERATING FINAL RECOMMENDATION
    print(f"OVERALL RECOMMENDATION OBJECT : \n  {overall_recommendation_object} \n")
    return InterviewFeedbackDataObject( 
        header =  header_object, 
        candidate_details =  candidate_details_object,
        evaluation_summary =  evaluation_summary_list_object,
        overall_recommendation =  overall_recommendation_object,
    )