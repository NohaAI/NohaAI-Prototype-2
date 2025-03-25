from src.dao.question import get_question_metadata
from src.services.llm.prompts.generate_evaluation_summary_prompt import generate_evaluation_summary_prompt_template
from src.services.llm import llm_service
import json
from src.utils import helper
from src.dao.question import fetch_question_by_ids
#TODO: generate_report should be prepare_interview_feedback - > gives data to create_pdf to create an interview_feedback report
def generate_evaluation_summary(question_id_list, chat_history, assessment_payloads, criteria_list):
    evaluation_summary_list = []
    questions_list = fetch_question_by_ids(question_id_list)
    for idx, question_id in enumerate(question_id_list):
        filtered_chat_history = helper.filter_chat_history(chat_history, question_id)
        # question = filtered_chat_history[0]["bot_dialogue"]
        question = questions_list[idx]
        criteria_scores = assessment_payloads[idx]["assessment_payload"][-1]["criteria_scores"]
        final_score = assessment_payloads[idx]["assessment_payload"][-1]["final_score"]    
        if len(criteria_scores) == 0: #if the candidate doesn't answer a questions criteria_scores would be an empty list
            criteria_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        llm_model = llm_service.get_openai_model()
        generate_evaluation_summary_prompt = generate_evaluation_summary_prompt_template()
        generate_evaluation_summary_chain = (generate_evaluation_summary_prompt | llm_model)
        llm_inputs = {
            'question': question,
            'chat_history': filtered_chat_history,
            'criteria_list': criteria_list
        }
        llm_response_generate_evaluation_summary = generate_evaluation_summary_chain.invoke(llm_inputs)
        llm_content_generate_evaluation_summary = json.loads(llm_response_generate_evaluation_summary.content)
        evaluation_summary_list.append((question, criteria_scores, final_score, llm_content_generate_evaluation_summary))
    return evaluation_summary_list