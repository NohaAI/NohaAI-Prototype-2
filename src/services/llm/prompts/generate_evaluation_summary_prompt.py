from langchain_core.prompts import ChatPromptTemplate

def generate_evaluation_summary_prompt_template_current():
  
  prompt="""
    Given:
    prompt_question: {question}
    prompt_chat_history: {chat_history}
    prompt_criteria_list: {criteria_list}

    Create a comprehensive evaluation report analyzing the candidate's performance on the given question. Return ONLY a valid Python dictionary with no additional text, markdown formatting, explanations, or quotes before or after. The dictionary must have the following structure:

    {{
        "evaluation_summary": {{
            "CRITERION_NAME": {{
                "Summary": "A detailed paragraph (3-5 sentences) summarizing how the candidate performed regarding this criterion, including specific examples from their response.",
                "Strengths": "A thorough description (3-5 sentences) of the candidate's strengths for this criterion, with concrete examples of what they did well.",
                "Weaknesses": "A comprehensive analysis (3-5 sentences) of the candidate's weaknesses or areas for improvement for this criterion, with specific examples.",
                "Judgment": "A balanced and nuanced assessment (3-5 sentences) of their overall performance for this criterion, including specific recommendations for improvement."
            }},
            "CRITERION_NAME":{{
                "Summary": "...",
                "Strengths": "...",
                "Weaknesses": "...",
                "Judgment": "..."
            }},
            ...
        }}
    }}

    Important formatting requirements:
    1. Format the output as a proper Python dictionary that can be directly evaluated
    2. Do not include any text outside the dictionary
    3. Do not use triple quotes, markdown formatting, or code blocks
    4. Ensure the output can be directly parsed by Python's eval() function
    5. Provide detailed, substantive content in each section (3-5 sentences minimum)
    6. Include specific examples from the candidate's responses in your evaluation
    7. Ensure evaluations are descriptive, analytical, and actionable
      """
  generate_evaluation_summary_prompt=ChatPromptTemplate.from_template(template=prompt)
  return generate_evaluation_summary_prompt

def generate_evaluation_summary_prompt_template():
  
  prompt="""
    Given:
    prompt_question: {question}
    prompt_chat_history: {chat_history}
    prompt_criteria_list: {criteria_list}

    Create a comprehensive evaluation report analyzing the candidate's performance on the given question. Return ONLY a valid Python dictionary with no additional text, markdown formatting, explanations, or quotes before or after. The dictionary must have the following structure:

    For each criterion in the prompt_criteria_list, create a shortened label by:
    - Using key nouns and adjectives from the criterion
    - Capitalizing the first letter of each major word
    - Keeping the label concise (2-4 words)

    {{
        "evaluation_summary": {{
            "SHORT_CRITERION_LABEL": {{
                "Summary": "A detailed paragraph (3-5 sentences) summarizing how the candidate performed regarding this criterion, including specific examples from their response.",
                "Strengths": "A thorough description (3-5 sentences) of the candidate's strengths for this criterion, with concrete examples of what they did well.",
                "Weaknesses": "A comprehensive analysis (3-5 sentences) of the candidate's weaknesses or areas for improvement for this criterion, with specific examples.",
                "Judgment": "A balanced and nuanced assessment (3-5 sentences) of their overall performance for this criterion, including specific recommendations for improvement."
            }},
            "SHORT_CRITERION_LABEL":{{
                "Summary": "...",
                "Strengths": "...",
                "Weaknesses": "...",
                "Judgment": "..."
            }},
            ...
        }}
    }}

    Important formatting requirements:
    1. Format the output as a proper Python dictionary that can be directly evaluated
    2. Do not include any text outside the dictionary
    3. Do not use triple quotes, markdown formatting, or code blocks
    4. Ensure the output can be directly parsed by Python's eval() function
    5. Provide detailed, substantive content in each section (3-5 sentences minimum)
    6. Include specific examples from the candidate's responses in your evaluation
    7. Ensure evaluations are descriptive, analytical, and actionable
      """
  generate_evaluation_summary_prompt=ChatPromptTemplate.from_template(template=prompt)
  return generate_evaluation_summary_prompt
