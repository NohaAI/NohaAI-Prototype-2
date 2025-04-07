from langchain_core.prompts import ChatPromptTemplate

def generate_evaluation_summary_prompt_template():
  prompt = """
    Given:
    prompt_question: {question}
    prompt_chat_history: {chat_history}
    prompt_criteria_list: {criteria_list}
    prompt_criteria_scores: {criteria_scores}
    prompt_question_score: {question_score}

    Create a comprehensive evaluation report analyzing the candidate's performance on the given question.

    Understanding the parameters:
    - prompt_question: The technical question posed to the candidate
    - prompt_chat_history: The complete conversation including the candidate's solution attempt
    - prompt_criteria_list: The evaluation criteria being used to assess performance
    - prompt_criteria_scores: Numerical scores for each criterion
    - prompt_question_score: Overall numerical score for the question  

    For each criterion in the prompt_criteria_list, create a shortened label by:
    - Using key nouns and adjectives from the criterion
    - Capitalizing the first letter of each major word
    - Keeping the label concise (2-4 words)

    The evaluation process should follow these steps:

    1. FIRST, carefully analyze prompt_chat_history to identify the candidate's solution attempt. Extract specific details about their approach, algorithm, code, or explanations.

    2. Review the prompt_criteria_scores (if available) to understand quantitative assessments for each criterion.

    Important formatting requirements:
        
    1. Base your evaluation SOLELY on what is present in the prompt_chat_history
    2. If prompt_criteria_scores are available, ensure your feedback aligns with these scores

    Your evaluation report should be returned as a dictionary with the following structure:

    Return a dictionary with EXACTLY this structure:

    {{
        "evaluation_summary": 
            {{
            "summary":"PARAGRAPH 1 providing an objective overview of how the candidate addressed all the criteria.",
            "strengths_weakness" : "PARAGRAPH 2 highlighting the candidate's specific strengths and weaknesses based on the criteria and their solution attempt."
            }}
    }}

    IMPORTANT:
    1.DO NOT include or reference any numerical scores or percentages in the evaluation text, even if they are provided in prompt_criteria_scores or prompt_question_score. 

    Important formatting requirements:
    
    1. Format the output as a proper Python dictionary that can be directly evaluated
    2. Do not include any text outside the dictionary
    3. Do not use triple quotes, markdown formatting, or code blocks
    4. Ensure the output can be directly parsed by Python's eval() function
    5. Base your evaluation SOLELY on what is present in the prompt_chat_history
    6. If prompt_criteria_scores are available, ensure your feedback aligns with these scores
    
    """
  prompt_current = """
    Given:
    prompt_question: {question}
    prompt_chat_history: {chat_history}
    prompt_criteria_list: {criteria_list}
    prompt_criteria_scores: {criteria_scores}
    prompt_question_score: {question_score}

    Create a comprehensive evaluation report analyzing the candidate's performance on the given question. Return ONLY a valid Python dictionary with no additional text, markdown formatting, explanations, or quotes before or after.

    Understanding the parameters:
    - prompt_question: The technical question posed to the candidate
    - prompt_chat_history: The complete conversation including the candidate's solution attempt
    - prompt_criteria_list: The evaluation criteria being used to assess performance
    - prompt_criteria_scores: Numerical scores for each criterion
    - prompt_question_score: Overall numerical score for the question  

    For each criterion in the prompt_criteria_list, create a shortened label by:
    - Using key nouns and adjectives from the criterion
    - Capitalizing the first letter of each major word
    - Keeping the label concise (2-4 words)

    Then create the evaluation dictionary with the following structure:

    {{
        "evaluation_summary": {{
            "SHORT_CRITERION_LABEL": {{
                "Summary": "[EVALUATION TEXT]",
                "Strengths": "[EVALUATION TEXT]",
                "Weaknesses": "[EVALUATION TEXT]",
                "Judgment": "[EVALUATION TEXT]"
            }},
            "SHORT_CRITERION_LABEL":{{
                "Summary": "[EVALUATION TEXT]",
                "Strengths": "[EVALUATION TEXT]",
                "Weaknesses": "[EVALUATION TEXT]",
                "Judgment": "[EVALUATION TEXT]"
            }},
            ...
        }}
   }}

    The evaluation process should follow these steps:

    1. FIRST, carefully analyze prompt_chat_history to identify the candidate's solution attempt. Extract specific details about their approach, algorithm, code, or explanations.

    2. Review the prompt_criteria_scores (if available) to understand quantitative assessments for each criterion.

    3. For each criterion, determine which of these scenarios applies:

    a. NO RESPONSE: The candidate did not provide any answer to the question at all.
        Use: 
        "Summary": "The candidate did not provide a response to this question. No substantive attempt was made to address this aspect of the problem.",
        "Strengths": "No strengths can be identified as the candidate did not provide a response to the question.",
        "Weaknesses": "The primary weakness is the lack of any response to the question. The candidate did not demonstrate an ability or willingness to engage with this problem.",
        "Judgment": "The candidate needs to provide at least an attempt at solving problems during technical interviews, even if the solution is imperfect. No assessment of technical abilities can be made without a response."

    b. CRITERION NOT ADDRESSED: The candidate provided a solution but did not address this specific criterion.
        Use:
        "Summary": "The candidate's solution did not address [SPECIFIC CRITERION DESCRIPTION]. While they provided an approach to the problem, they did not explicitly consider this aspect in their solution.",
        "Strengths": "No strengths can be identified specifically for this criterion as it was not addressed in the candidate's solution.",
        "Weaknesses": "The candidate did not demonstrate consideration of [SPECIFIC CRITERION DESCRIPTION], which is necessary for a complete technical solution.",
        "Judgment": "To improve, the candidate should explicitly address [SPECIFIC CRITERION DESCRIPTION] when approaching similar problems, as this demonstrates thorough technical understanding."

    c. CRITERION ADDRESSED: The candidate addressed this criterion in their solution.
        Provide a detailed evaluation using:
        - Specific quotes or paraphrases from the candidate's solution
        - Examples of what they did correctly or incorrectly
        - Detailed analysis (3-5 sentences per section)
        - References to technical concepts relevant to that criterion
        - If available, incorporate the prompt_criteria_scores to calibrate your feedback

    4. When evaluating a criterion that was addressed, be specific and substantive:
    - Summary: Provide an objective overview of how the candidate addressed this criterion
    - Strengths: Identify specific aspects they handled well with concrete examples
    - Weaknesses: Identify specific aspects they could improve with concrete examples
    - Judgment: Provide balanced feedback with specific recommendations

    Important formatting requirements:
    1. Format the output as a proper Python dictionary that can be directly evaluated
    2. Do not include any text outside the dictionary
    3. Do not use triple quotes, markdown formatting, or code blocks
    4. Ensure the output can be directly parsed by Python's eval() function
    5. Base your evaluation SOLELY on what is present in the prompt_chat_history
    6. If prompt_criteria_scores are available, ensure your feedback aligns with these scores
    """
  generate_evaluation_summary_prompt=ChatPromptTemplate.from_template(template=prompt)
  return generate_evaluation_summary_prompt
