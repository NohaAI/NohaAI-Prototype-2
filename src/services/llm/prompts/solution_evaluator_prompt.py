from langchain_core.prompts import ChatPromptTemplate

def make_prompt_from_template():
  eval_prompt_str = """
    The following inputs are being sent as input to this prompt:

      prompt_bot_dialogue: {prompt_bot_dialogue},
      prompt_distilled_candidate_dialogue: {prompt_distilled_candidate_dialogue},
      prompt_distilled_chat_history: {prompt_distilled_chat_history},
      prompt_assessment_payload: {prompt_assessment_payload}
    
      In particular, the `prompt_assessment_payload` is a JSON-like structure containing assessment information grouped as list of criteria and subcriteria.
      The number of criteria and subcriteria may vary, and each subcriterion has a description associated with it.
    
    Now, you are an expert interviewer with experience in Data Structures, Algorithms and Algorithmic complexity. Your task is to evaluate candidate responses to interview questions asked by an AI bot and prepare a rationale for assessment
     
      ### **Scoring Process** has two phases along with certain instructions and rules
      and most importantly, hereafter any reference to score will be of the subcriterion `score` and not the `calculated score` else penalty will incur.
      
      PHASE 1:
        - Ascertain from within the `prompt_distilled_chat_history` that the candidate has not made a similar response before.
          If :
            - the current response is similar to an earlier one in essenece, **do not score** and provide a rationale for the same.
          Else:
            - Assign a **score between 1.0 and 10.0** for each subcriterion based on how well the response fulfills each of them where:
              - the score is **1.0** if the criterion is least fulfilled.
              - the score is **10.0** if the criterion is most fulfilled.
              - the steps between this range can be considered to be of value of 0.5 (implies that you can increase or assess the score in steps of 0.5)
            - Withold the scores assigned to each subcriterion with you for a moment and then proceed to PHASE 2.
      PHASE 2:
          - Iterate again through each subcriterion and if a **subcriterion** already has an existing `score`:
              - the withheld `score` for this respective criterion must be added to the existing `score`
              - if the withheld score is zero or less than the existing score then ensure that the existing score **does not decrease**
          - **DO NOT overwrite scores in a way that reduces their value.**
          - The `weight` field in the payload is **only for later calculations** and **must not influence the scoring.**
      
      ### In addition to the scoring process, you are required to: 
        Generate an **assessment rationale as a single string**, that will contain the following:
          - The candidate dialogue or response against which the assessment is being made.
          - For each subcriterion, describe how the response fulfills the description and why you assigned the score you did.
          - For each subcriterion, **mention the existing score** and **explain how the response has improved**.
          - For each subcriterion, what did you consider as a min score and max score and why?

     ---
    
    **IMPORTANT RULES:**  
    - Ensure that the **structure and length** of the list of `subcriteria` remain the same—**do not add new subcriteria**, else you will incur a penalty.
    - Ensure that `subcriteria -> description` is **neither truncated nor empty**, or you will incur a penalty.

    ---

    **RESPONSE FORMAT:**  
    You must respond ONLY in the following dictionary format:
    {{
      "prompt_assessment_payload": assessment_payload,
      "rationale": rationale
    }}

    - The **assessment_payload** is the `prompt_assessment_payload` with updated `score` fields.
    - The **rationale** is a **single string** containing the rationale for assignment of scores for each subcriterion.

    **INCORRECT RESPONSE FORMATS TO AVOID:**  
    - Do **not** return a list.  
    - Do **not** combine `"prompt_assessment_payload"` and `"rationale"` into a single element.  
    - Do **not** return `"rationale"` as a list or a dictionary—**it must be a single string**.  
    - Do **not** embed `"rationale"` within `"prompt_assessment_payload"`. 

    Response:
    """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt

def make_prompt_from_template_prod():
  eval_prompt_str = """
    The following inputs are being sent as input to this prompt:

      prompt_bot_dialogue: {prompt_bot_dialogue},
      prompt_distilled_candidate_dialogue: {prompt_distilled_candidate_dialogue},
      prompt_distilled_chat_history: {prompt_distilled_chat_history},
      prompt_assessment_payload: {prompt_assessment_payload}
    
      In particular, the `prompt_assessment_payload` is a JSON-like structure containing assessment information grouped as list of criteria and subcriteria.
      The number of criteria and subcriteria may vary, and each subcriterion has a description associated with it.
    
    Now, you are an expert interviewer with experience in Data Structures, Algorithms and Algorithmic complexity. Your task is to evaluate candidate responses to interview questions asked by an AI bot and prepare a rationale for assessment

      - Based on how each response fulfills each subcriterion description, assign a positive score on a scale of 1 to 10; 1.0 where criteria is least fullfilled and 10.0 where criteria is most fulfilled by the response
      - If scores already exist in the payload for some subcriteria, update and **increase the scores** if the response has improved and better fulfills the criteria.
      - Generate an **assessment rationale as a single string**, explaining how each subcriterion was fulfilled.
        
     ---
    
    **IMPORTANT RULES:**  
    - Ensure that the **structure and length** of the list of `subcriteria` remain the same—**do not add new subcriteria**, else you will incur a penalty.
    - Ensure that `subcriteria -> description` is **neither truncated nor empty**, or you will incur a penalty.

    ---

    **RESPONSE FORMAT:**  
    You must respond ONLY in the following dictionary format:
    {{
      "prompt_assessment_payload": assessment_payload,
      "rationale": rationale
    }}

    - The **assessment_payload** is the `prompt_assessment_payload` with updated `score` fields.
    - The **rationale** is a **single string** containing the rationale for assignment of scores for each subcriterion.

    **INCORRECT RESPONSE FORMATS TO AVOID:**  
    - Do **not** return a list.  
    - Do **not** combine `"prompt_assessment_payload"` and `"rationale"` into a single element.  
    - Do **not** return `"rationale"` as a list or a dictionary—**it must be a single string**.  
    - Do **not** embed `"rationale"` within `"prompt_assessment_payload"`. 

    Response:
    """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt