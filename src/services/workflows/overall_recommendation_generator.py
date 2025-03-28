from src.services.llm import llm_service
from src.services.llm.prompts.generate_overall_recommendation_prompt import generate_overall_recommendation_prompt_template
import json
def generate_overall_recommendation(evaluation_summary_list, criteria_list):
    llm_model = llm_service.get_openai_model()
    generate_overall_recommendation_prompt = generate_overall_recommendation_prompt_template()
    generate_overall_recommendation_chain = (generate_overall_recommendation_prompt | llm_model)

    criteria_list = []
    
    llm_inputs = {
        'evaluation_summary_list': evaluation_summary_list,
        'criteria_list': criteria_list
    }
    llm_response_overall_recommendation = generate_overall_recommendation_chain.invoke(llm_inputs)
    llm_content_overall_recommendation = llm_response_overall_recommendation.content
    overall_recommendation = llm_content_overall_recommendation
    return overall_recommendation
