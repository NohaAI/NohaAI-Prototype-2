from src.services.llm import llm_service
from src.services.llm.prompts.generate_interview_summary_and_recommendation_prompt import generate_interview_summary_and_recommendation_template
import json
def generate_interview_summary_and_recommendation(evaluation_summary_list, criteria_list):
    llm_model = llm_service.get_openai_model()
    generate_interview_summary_and_recommendation_prompt = generate_interview_summary_and_recommendation_template()
    generate_interview_summary_and_recommendation_chain = (generate_interview_summary_and_recommendation_prompt | llm_model)

    criteria_list = []
    
    llm_inputs = {
        'evaluation_summary_list': evaluation_summary_list,
        'criteria_list': criteria_list
    }
    llm_response_interview_summary_and_recommendation = generate_interview_summary_and_recommendation_chain.invoke(llm_inputs)
    llm_content_interview_summary_and_recommendation = llm_response_interview_summary_and_recommendation.content
    interview_summary_and_recommendation = json.loads(llm_content_interview_summary_and_recommendation)
    return interview_summary_and_recommendation
