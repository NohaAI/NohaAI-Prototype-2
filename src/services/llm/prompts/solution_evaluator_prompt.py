from langchain_core.prompts import ChatPromptTemplate

def make_prompt_from_template_to_be_pushed():
  eval_prompt_str = """
    The following inputs are being sent as input to this prompt:

      prompt_bot_dialogue: {prompt_bot_dialogue},
      prompt_distilled_candidate_dialogue: {prompt_distilled_candidate_dialogue},
      prompt_distilled_chat_history: {prompt_distilled_chat_history},
      prompt_assessment_payload: {prompt_assessment_payload}
    
      In particular, the prompt_assessment_payload is a JSON like structure containing assessment information grouped as list of criteria and subcriteria 
      Note that the number of criteria and subcriteria may vary and that each subcriteria has a description associated with it.
    
    Now, you are an expert interviewer with experience in Data Structures, Algorithms and Algorithmic complexity. Your task is to evaluate a candidate responses to interview questions asked by an AI bot and prepare a rationale for assessment
      * Based on how each response fulfills each subcriterion description assign a positive score on a scale of 1 to 10; 1.0 where criteria is least fullfilled and 10.0 where criteria is most fulfilled by the response
      * Append the assessment rationale for each subcriterion description in a variable "rationale" indexed from 1 onwards
        
    **IMPORTANT:** 
    - Ensure that the **structure and length** of the list of `subcriteria` remain the same—no new `subcriterion` should be added, else you will incur a penalty.
    - Ensure that `subcriteria` -> `description` is **neither truncated nor empty**, or you will incur a penalty.

    **RESPONSE FORMAT:**  
    You must respond ONLY in the following dictionary format:
    {{
      "prompt_assessment_payload": assessment_payload,
      "rationale": rationale
    }}
      
    ]
    - The **assessment_payload** is the `prompt_assessment_payload` with updated `score` fields.
    - The **rationale** is a string containing the rationale for assignment of scores for each subcriterion
    
    **INCORRECT RESPONSE FORMATS TO AVOID:**  
    - Do **not** combine `"prompt_assessment_payload"` and `"rationale"` into a single element.
    - Do **not** return more than two elements in the list.
    - Do **not** embed `"rationale"` within `"prompt_assessment_payload"`.

    Response:
    """
  
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt

def make_prompt_from_template():
  eval_prompt_str = """
    The following inputs are being sent as input to this prompt:

      prompt_bot_dialogue: {prompt_bot_dialogue},
      prompt_distilled_candidate_dialogue: {prompt_distilled_candidate_dialogue},
      prompt_distilled_chat_history: {prompt_distilled_chat_history},
      prompt_assessment_payload: {prompt_assessment_payload}
    
      In particular, the prompt_assessment_payload is a JSON like structure containing assessment information grouped as list of criteria and subcriteria 
      Note that the number of criteria and subcriteria may vary and that each subcriteria has a description associated with it.
    
    Now, you are an expert interviewer with experience in Data Structures, Algorithms and Algorithmic complexity. Your task is to evaluate a candidate responses to interview questions asked by an AI bot and prepare a rationale for assessment
      * Based on how each response fulfills each subcriterion description assign a positive score on a scale of 1 to 10; 1.0 where criteria is least fullfilled and 10.0 where criteria is most fulfilled by the response
      * If scores already exist in the payload for some subcriteria then increase and update the scores if the response has improved and better fulfills the criteria
      * Append the assessment rationale for each subcriterion description in a variable "rationale" indexed from 1 onwards
        
    **IMPORTANT:** 
    - Ensure that the **structure and length** of the list of `subcriteria` remain the same—no new `subcriterion` should be added, else you will incur a penalty.
    - Ensure that `subcriteria` -> `description` is **neither truncated nor empty**, or you will incur a penalty.

    **RESPONSE FORMAT:**  
    You must respond ONLY in the following dictionary format:
    {{
      "prompt_assessment_payload": assessment_payload,
      "rationale": rationale
    }}
      
    ]
    - The **assessment_payload** is the `prompt_assessment_payload` with updated `score` fields.
    - The **rationale** is a string containing the rationale for assignment of scores for each subcriterion
    
    **INCORRECT RESPONSE FORMATS TO AVOID:**  
    - Do **not** combine `"prompt_assessment_payload"` and `"rationale"` into a single element.
    - Do **not** return more than two elements in the list.
    - Do **not** embed `"rationale"` within `"prompt_assessment_payload"`.

    Response:
    """
  
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt