from src.dao.interview import get_candidate_details
from src.config import constants as const
from datetime import datetime
from typing import List
from src.utils import helper
from src.services.workflows.evaluation_summary_generator import generate_evaluation_summary
from src.schemas.interview_evaluation import HeaderObject, CandidateDetailItem, EvaluationSummaryObject, OverallRecommendationObject, InterviewEvaluationDataObject
from src.services.workflows.overall_recommendation_generator import generate_overall_recommendation

def create_criteria_list(assessment_payloads):
    assessment_payload = assessment_payloads[0] #pick any assessment_payload since all have the same criteria
    criteria_list = []
    for criterion in assessment_payload['assessment_payloads'][-1]['criteria']:
        criteria_list.append(criterion['description'])
    return criteria_list

def create_header_object() -> HeaderObject:
    
    return HeaderObject(
        title = "Interview Feedback",
        position = {"x": 200, "y": 50},
        font = {"name": "Helvetica-Bold", "size": 16}
    )

def create_candidate_details_object(session_state, assessment_payloads) -> List[CandidateDetailItem]:
    
    interview_id = session_state['interview_id']
    #interview_id = 1027 # FOR TESTING 
    candidate_details = get_candidate_details(interview_id)
    candidate_name = candidate_details['name']
    interview_date_obj = candidate_details['interview_date']
    interview_date = interview_date_obj.date()
    interview_time = interview_date_obj.time().strftime("%H:%M:%S")
    report_generation_date = datetime.now().date()
    overall_score,total_possible_score = helper.calculate_overall_score(assessment_payloads)
    candidate_details_object = [
        CandidateDetailItem(label= "Candidate Name", value= candidate_name),
        CandidateDetailItem(label= "Interview ID", value= interview_id),
        CandidateDetailItem(label= "Date", value= interview_date),
        CandidateDetailItem(label= "Time", value= interview_time),
        CandidateDetailItem(label= "Interview Conducted By", value= const.BOT_NAME),
        CandidateDetailItem(label= "Overall Score", value= f"{overall_score}/{total_possible_score}")
    ]
    return candidate_details_object

def create_evaluation_summary_object_list(session_state, chat_history, assessment_payloads, criteria_list ,code_snippet) -> List[EvaluationSummaryObject]:
    evaluation_summary_object_list = []
    
    evaluation_summary_list = generate_evaluation_summary(session_state['questions_asked'], chat_history, assessment_payloads, criteria_list)
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
    
def prepare_interview_evaluation_data(session_state, chat_history, assessment_payloads,code_snippet = None) -> InterviewEvaluationDataObject:
    try:
        if not code_snippet or code_snippet == []:
            code_snippet = []
            for i in range(len(assessment_payloads)):
                code_snippet.append("NO CODE SNIPPET PROVIDED")
        criteria_list = create_criteria_list(assessment_payloads) #helper func to get the list of criteria
        #TODO: DB can be used instead of a helper func
        header_object = create_header_object()
        
        candidate_details_object = create_candidate_details_object(session_state, assessment_payloads)
        
        evaluation_summary_object_list = create_evaluation_summary_object_list(session_state, chat_history, assessment_payloads, criteria_list,code_snippet)
        
        overall_recommendation_object = create_overall_recommendation_object(evaluation_summary_object_list, criteria_list) 
        
        return InterviewEvaluationDataObject( 
            header_object =  header_object, 
            candidate_details_object =  candidate_details_object,
            evaluation_summary_object_list =  evaluation_summary_object_list,
            overall_recommendation_object =  overall_recommendation_object,
        )
    except Exception as e:
        print(f"ERROR OCCERED WHILE PREPARING DATA USING SESSION_STATE : {e}")
        raise e