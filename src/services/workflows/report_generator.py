from src.dao.question import get_question_metadata
from src.services.llm.prompts.generate_report_prompt import generate_report_prompt_template
from src.services.llm import llm_service
import json
from src.utils import helper
#TODO: generate_report should be prepare_interview_feedback - > gives data to create_pdf to create an interview_feedback report
async def prepare_interview_feedback(questions_asked, chat_history, assessment_payloads):
    counter = 0
    criteria_list = ["Assumptions clarification", "Corner cases handeling", "Data structure choice", "Algorithm choice", "Time complexity", "space complexity"]
    for question_id in questions_asked:
        filtered_chat_history = helper.filter_chat_history(chat_history, question_id)
        question = filtered_chat_history[0]["bot_dialogue"]
        criteria_scores = assessment_payloads[counter]["assessment_payload"]["criteria_scores"]
        final_score = assessment_payloads[counter]["assessment_payload"]["final_score"]
        counter += 1
        if len(criteria_scores) == 0:
            criteria_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        print(f"QUESTION : \n {question} \n ")
        print(f"FILTERED CHAT HISTORY : \n {filtered_chat_history} \n ")
        print(f"CRITERIA SCORES : \n {criteria_scores} \n ")
        print(f"FINAL SCORE : \n {final_score} \n ")
        llm_model = llm_service.get_openai_model()
        generate_report_prompt = generate_report_prompt_template()
        generate_report_chain = (generate_report_prompt | llm_model)
        llm_inputs = {
            'question': question,
            'chat_history': filtered_chat_history,
            'criteria_list': criteria_list
        }
        llm_response_generate_report = await generate_report_chain.ainvoke(llm_inputs)
        llm_content_generate_report = json.loads(llm_response_generate_report.content)
        print(f"REPORT CONTENT FOR QUESTION {question} : \n {llm_content_generate_report} \n")
        interview_feedback_data= []