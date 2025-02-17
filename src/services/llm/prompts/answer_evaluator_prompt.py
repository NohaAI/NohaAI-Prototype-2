from langchain_core.prompts import ChatPromptTemplate

def make_prompt_from_template():
  eval_prompt_str = """
    You are an expert interviewer with experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
      eval_distribution: {eval_distribution}
    
    Please evaluate the response based on the following evaluation guidelines:
    1. Group the subcriteria received in the subcriteria payload above into seven consecutive groups of three each
    2.For each subcriterion in the subcriteria received above, pl. give a score between 1-10 for the response depending on how much the response fulfills the subcriterion
    
    IMPORTANT : 
    - Please ensure that the structure and length of the subcriteria remain the same and no new subcriterion are added because you would incur a penalty otherwise
    
    - Make sure no subcriterion question is truncated because the subcriterion question is used as a key in one of the dictionaries for later processing
    
    YOU MUST RESPOND IN THE FOLLOWING LIST FORMAT:
    [
      "answer_evaluation",
      "rationale"
    ]
    YOU MUST RESPOND WITH A LIST CONTAINING EXACTLY TWO ELEMENTS:
    1. The first element must be a dictionary containing the answer evaluation scores
    2. The second element must be a string containing the rationale

    The answer_evaluation dictionary must be in strict JSON format.
    
    Example:
    [
        {{
            "Subcriterion question": "8",
            "Subcriterion question": "3",
            "Subcriterion question": "6"
        }},
        "rationale"
    ]
    INCORRECT response formats to avoid:
  - Do not combine the evaluation and rationale into a single element
  - Do not return more than two elements in the list
  - Do not embed the rationale within the evaluation dictionary

  Response:
    """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt

def make_prompt_from_template_precentage_driven():
  eval_prompt_str = """
    You are an expert interviewer with experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
      eval_distribution: {eval_distribution}
    
    Please evaluate the response based on the following evaluation guidelines:
    1. Group the subcriteria received in the subcriteria payload above into seven consecutive groups of three each
    2. Please evaluate the answer as per the instructions provided in each subcriterion and convert the percentage scores to a 0-10 scale as follows:
      - If a criterion awards X%, convert it to (X/10) points
      - Examples:
        * 100% = 10 points
        * 50% = 5 points
        * 40% = 4 points
        * 25% = 2.5 points
        * 13% = 1.3 points
        * 0% = 0 points
    
    IMPORTANT : 
    - Please ensure that the structure and length of the subcriteria remain the same and no new subcriterion are added because you would incur a penalty otherwise
    
    - Make sure no subcriterion question is truncated because the subcriterion question is used as a key in one of the dictionaries for later processing
    
    YOU MUST RESPOND IN THE FOLLOWING LIST FORMAT:
    [
      "answer_evaluation",
      "rationale"
    ]
    YOU MUST RESPOND WITH A LIST CONTAINING EXACTLY TWO ELEMENTS:
    1. The first element must be a dictionary containing the answer evaluation scores
    2. The second element must be a string containing the rationale

    The answer_evaluation dictionary must be in strict JSON format.
    
    Example:
    [
        {{
            "Subcriterion question": "8",
            "Subcriterion question": "3",
            "Subcriterion question": "6"
        }},
        "rationale"
    ]
    INCORRECT response formats to avoid:
  - Do not combine the evaluation and rationale into a single element
  - Do not return more than two elements in the list
  - Do not embed the rationale within the evaluation dictionary

  Response:
    """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt
