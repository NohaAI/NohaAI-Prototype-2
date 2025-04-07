from langchain_core.prompts import ChatPromptTemplate

def generate_interview_summary_and_recommendation_template():
    prompt = """
    Given: 
    prompt_evaluation_summary_list: {evaluation_summary_list}
    prompt_criteria_list: {criteria_list}

    Analyze the candidate's performance on DSA questions and provide a structured assessment.

    For each question in evaluation_summary_list:
    1. Extract key points from the existing evaluation_summary
    2. Reference the question_score provided
    3. Calculate the average score across all questions (for your reference only)

    Return a dictionary in the following format:
    {{
        "interview_summary": "A brief 50-100 word summary of the candidate's performance across all questions, noting any patterns, strengths, and weaknesses observed during the interview",
        "overall_recommendation": "A personalized 50-100 word verdict that addresses whether you would recommend hiring the candidate, with brief justification for your recommendation. Use natural language appropriate for a hiring manager while maintaining a professional tone."
    }}
    The assessment should provide a thoughtful, human-like conclusion about the candidate's suitability without disclosing any numerical scores.

    Important formatting requirements:
    
    1. Format the output as a proper Python dictionary that can be directly evaluated
    2. Do not include any text outside the dictionary
    3. Do not use triple quotes, markdown formatting, or code blocks

    """
    prompt_current="""
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
    3. Calculate the average score across all questions (for your reference only)

    Return a single paragraph (100-150 words) that:
    1. Briefly summarizes performance on each question using the most significant points from the existing evaluations
    2. Notes any patterns across questions (consistent strengths or weaknesses)
    3. Concludes with a personalized verdict that:
     - Uses natural language appropriate for a hiring manager or technical interviewer
     - Directly addresses whether you would recommend hiring the candidate
     - Provides brief justification for your recommendation
     - Maintains a professional tone
     - Is informed by the calculated average score range (≥8, 6-8, 4-6, or <4) but expresses the verdict in your own words
     - Avoids formulaic language or fixed phrases
     - Sounds like a thoughtful human judgment

    The assessment should maintain a professional tone while providing a thoughtful, human-like conclusion about the candidate's suitability without disclosing any numerical scores.

    """
    prompt_with_scores="""
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
