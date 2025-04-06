from src.dao.interview import get_candidate_details
from src.config import constants as const
from datetime import datetime
from typing import List
from src.utils import helper
from src.services.workflows.evaluation_summary_generator import generate_evaluation_summary
from src.schemas.interview_evaluation import HeaderObject, CandidateDetailItem, EvaluationSummaryObject, OverallRecommendationObject, InterviewEvaluationDataObject, AppendixObject
from src.services.workflows.overall_recommendation_generator import generate_overall_recommendation

def create_criteria_list(assessment):
    assessment_record = assessment[0] #pick any assessment_payload since all have the same criteria
    criteria_list = []
    for criterion in assessment_record['assessment_payloads'][-1]['criteria']:
        criteria_list.append(criterion['description'])
    criteria_list[0], criteria_list[3] = criteria_list[3], criteria_list[0] #swaps criteria in the following order [algo, ds, assump, corner, time, space, comms] 
    criteria_list[1], criteria_list[2] = criteria_list[2], criteria_list[1]
    return criteria_list

def create_header_object() -> HeaderObject:
    
    return HeaderObject(
        title = "Interview Feedback",
        position = {"x": 200, "y": 50},
        font = {"name": "Helvetica-Bold", "size": 16}
    )

def create_candidate_details_object(session_state) -> List[CandidateDetailItem]:
    
    interview_id = session_state['interview_id']
    #interview_id = 1027 # FOR TESTING 
    candidate_details = get_candidate_details(interview_id)
    candidate_name = candidate_details['name']
    interview_date_obj = candidate_details['interview_date']
    interview_date = interview_date_obj.date()
    interview_time = interview_date_obj.time().strftime("%H:%M:%S")
    report_generation_date = datetime.now(const.IST).date()
    # overall_score,total_possible_score = helper.calculate_overall_score(assessment_payloads)
    candidate_details_object = [
        CandidateDetailItem(label= "Candidate Name", value= candidate_name),
        CandidateDetailItem(label= "Interview ID", value= interview_id),
        CandidateDetailItem(label= "Date", value= interview_date),
        CandidateDetailItem(label= "Time", value= interview_time),
        CandidateDetailItem(label= "Interview Conducted By", value= const.BOT_NAME),
        #CandidateDetailItem(label= "Overall Score", value= f"{overall_score}/{total_possible_score}")
    ]
    return candidate_details_object

def create_evaluation_summary_object_list(session_state, chat_history, assessment_payloads, criteria_list) -> List[EvaluationSummaryObject]:
    evaluation_summary_object_list = []
    
    evaluation_summary_list = generate_evaluation_summary(session_state['questions_asked'], chat_history, assessment_payloads, criteria_list)
    #preparing list of EvaluationSummaryObject
    for i, (question, criteria_scores, question_score, evaluation_summary) in enumerate(evaluation_summary_list):
        evaluation_object = EvaluationSummaryObject(
            question_number = i+1,
            question = question,
            evaluation_summary = evaluation_summary,
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

def create_appendix_object(candidate_name, chat_history ,code_snippet, video_url = "N/A") -> AppendixObject:
    chat_history_list = []
    for chat_history_record in chat_history:
        chat_history_list.append({
        "Noha": chat_history_record['bot_dialogue'],
        f"{candidate_name}": chat_history_record['distilled_candidate_dialogue']
    })
        
    return AppendixObject(
        code_snippet = code_snippet,
        chat_history = chat_history_list,
        video_url = video_url
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
        
        candidate_details_object = create_candidate_details_object(session_state)
        
        evaluation_summary_object_list = create_evaluation_summary_object_list(session_state, chat_history, assessment_payloads, criteria_list)

        appendix_object = create_appendix_object(candidate_details_object[0].value, chat_history, code_snippet)
        
        if assessment_payloads[0]["assessment_payloads"][-1]["final_score"] == 0:
            overall_recommendation_object = OverallRecommendationObject (title =  "OVERALL RECOMMENDATION:", content = None)
        else:
            overall_recommendation_object = create_overall_recommendation_object(evaluation_summary_object_list, criteria_list) 
        
        return InterviewEvaluationDataObject( 
            header_object =  header_object, 
            candidate_details_object =  candidate_details_object,
            evaluation_summary_object_list =  evaluation_summary_object_list,
            overall_recommendation_object =  overall_recommendation_object,
            appendix_object = appendix_object
        )
    except Exception as e:
        print(f"ERROR OCCERED WHILE PREPARING DATA USING SESSION_STATE : {e}")
        raise e