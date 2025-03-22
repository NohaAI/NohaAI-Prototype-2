from src.dao.question import get_question_metadata
from src.services.llm.prompts.generate_evaluation_summary_prompt import generate_evaluation_summary_prompt_template
from src.services.llm import llm_service
import json
from src.utils import helper
#TODO: generate_report should be prepare_interview_feedback - > gives data to create_pdf to create an interview_feedback report
def generate_evaluation_summary(session_state, chat_history, assessment_payloads, criteria_list):
    evaluation_summary_list = []
    questions_asked = session_state['questions_asked']
    for idx, question_id in enumerate(questions_asked):
        filtered_chat_history = helper.filter_chat_history(chat_history, question_id)
        question = filtered_chat_history[0]["bot_dialogue"]
        criteria_scores = assessment_payloads[idx]["assessment_payload"]["criteria_scores"]
        final_score = assessment_payloads[idx]["assessment_payload"]["final_score"]    
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
        print(f"REPORT CONTENT FOR QUESTION {question} : \n {llm_content_generate_evaluation_summary} \n")
    print(f"EVALUATION SUMMARY LIST : \n {evaluation_summary_list}")
    return evaluation_summary_list