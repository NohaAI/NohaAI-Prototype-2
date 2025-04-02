from langchain_core.prompts import ChatPromptTemplate

def generate_overall_recommendation_prompt_template():
  
    prompt="""
    Given: 
    prompt_evaluation_summary_list: {evaluation_summary_list}
    prompt_criteria_list: {criteria_list}

    Analyze the candidate's performance on DSA questions and provide a brief assessment.

    Given: 
    prompt_evaluation_summary_list: {evaluation_summary_list}
    prompt_criteria_list: {criteria_list}

    Generate a concise assessment of the candidate's suitability based on their DSA question performance.

    For each question in evaluation_summary_list:
    1. Extract key points from the existing evaluation_summary
    2. Reference the question_score provided

    Calculate the average score across all questions.

    Return a single paragraph (100-150 words) that:
    1. Briefly summarizes performance on each question using the most significant points from the existing evaluations
    2. Notes any patterns across questions (consistent strengths or weaknesses)
    3. States the calculated average score
    4. Concludes with a personalized verdict that:
     - Uses natural language appropriate for a hiring manager or technical interviewer
     - Directly addresses whether you would recommend hiring the candidate
     - Provides brief justification for your recommendation
     - Maintains a professional tone
     - Is informed by the calculated average score range (≥8, 6-8, 4-6, or <4) but expresses the verdict in your own words
     - Avoids formulaic language or fixed phrases
     - Sounds like a thoughtful human judgment

    The assessment should maintain a professional tone while providing a thoughtful, human-like conclusion about the candidate's suitability.

    """
  
    generate_overall_recommendation_prompt=ChatPromptTemplate.from_template(template=prompt)
    return generate_overall_recommendation_prompt
