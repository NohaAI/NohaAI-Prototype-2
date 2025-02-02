from langchain_core.prompts import ChatPromptTemplate

# def make_prompt_from_template():
#     eval_prompt_str = """
#         You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
#         Given the following inputs:
#             question: {question}
#             answer: {answer}
#             chat_history: {chat_history}
#             subcriteria: {subcriteria}

#        Your task is to score the answer against each criterion between 1 to 10 (1 when the answer least fulfills the criterion and 10 when it fulfills completely)
       
#         Example:
#         {{
#             "I might try the double pointer approach which might help due to the symmetry in a palindrome string": [
#                 {{"subcriterion": "Is a string sufficient to solve the problem, or is another data structure required?", 
#                 "score": 3
#                 }},
#                 {{
#                 "subcriterion": "Does the candidate consider the use of a stack or two-pointer technique?", 
#                 "score": 9
#                 }},
#                 {{"subcriterion":"Has the candidate evaluated the need for auxiliary storage?", 
#                 "score": 1
#                 }}
#             ],
#             "I might try the double pointer approach which might help due to the symmetry in a palindrome string": [
#                 {{"subcriterion": "Does the candidates solution use O(1) space, or is additional space necessary?": 8
#                 }},
#                 {{
#                 "subcriterion": "Is there any mention of the space used by auxiliary data structures?", 
#                 "score": 2
#                 }},
#                 {{"subcriterion":"Has the candidate considered the implications of creating copies of the string?", 
#                 "score": 4
#                 }}
#             ]
#         }}


#         Response: 
#     """
#     eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
#     return eval_prompt




# def make_prompt_from_template():
#     eval_prompt_str = """
#         You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
#         Given an interview question and a candidate's answer your task is as follows:
#         1. At first, pls. ensure if there is a chat history related to the above question/answer pair in chat_history
#         2. If chat history does not exist then pls. score the candidate's answer according to how it measures up against the following set of criteria 
#         3. If chat history exists, then pl. rescore the answer while also considering the chat history
#         4. Overall, pls. give the answer against each criterion a score between 1 to 10

#         Input is in the form as follows.
#         question: {question}
#         answer: {answer}
#         chat_history: {chat_history}
#         subcriteria: {subcriteria}
        
#         An example JSON format for the output is as follows.
#         {{"What will be the approach to check if a string is a palindrome.": [ 
#                 {{"I might try the double pointer approach which might help due to the symmetry in a palindrome string": [
#                     {{"subcriterion": "Is a string sufficient to solve the problem, or is another data structure required?", "score": 3}},
#                     {{"subcriterion": "Does the candidate consider the use of a stack or two-pointer technique?", "score": 9}},
#                     {{"subcriterion":"Has the candidate evaluated the need for auxiliary storage?", "score": 1}}
#                 ]
#                 }}
#         ]
#         }}
#     """
#     eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
#     return eval_prompt

def make_prompt_from_template_16Jan2025():
  eval_prompt_str = """
    You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
	  eval_distribution: {eval_distribution}
	The chat_history is a sequence of question/answer pairs, each pair representing a conversation turn between the interviewer and candidate respectively. Please take into account all previous answers in the chat_history along with the recent most answer and collectively score against each criterion between 1 to 10 (1 when the answer least fulfills the criterion and 10 when it fulfills completely)
    
    The response must be in strict JSON format as given in the example below.
    Example:
    {{
        "Has the candidate considered the scenario of an empty set?": "2",
        "Does the solution handle cases where the target sum exceeds the sum of all elements in the set?": "2",
        "Has the candidate explained the scenario where no valid subset exists?": "1"
    }},
    {{
        "Is a string sufficient to solve the problem, or is another data structure required?": "3",
        "Does the solution handle cases where the target sum exceeds the sum of all elements in the set?": "2"
        "Is there consideration for the smallest possible target sum that can be achieved?": "3"
    }}
    Response:
  """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt

def make_prompt_from_template_Ritesh():
  eval_prompt_str = """
    You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
	    eval_distribution: {eval_distribution}
	  The chat_history is a sequence of question/answer pairs, each pair representing a conversation turn between the interviewer and candidate respectively. You have been provided the recent most candidate question and answer, the chat_history and the subcriteria(collection of subcriterion) for assessment. Please take into account all previous answers in the chat_history and collectively score the recent most candidate answer against each sub-criterion between 1 to 10 (1 when the answer least fulfills the criterion and 10 when it fulfills completely). Pl. ensure that the structure and length of the subcriteria remain the same and no new subcriterion are added because you would incur a penalty otherwise.
    
    The response must be in strict JSON format as given in the example below.
    Example:
    {{
        "Subcriterion question": "4",
        "Subcriterion question": "4",
        "Subcriterion question": "2"
    }}
    Response:
  """
def make_prompt_from_template():
  eval_prompt_str = """
    You are an expert interviewer with experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    
    
    EVALUATION GUIDELINES:
    1. Only evaluate and score subcriteria that the candidate has EXPLICITLY addressed in their answers
    2. For any subcriterion that the candidate has not EXPLICITLY addressed, assign a score of 1
    3. If the solution contains best practices and is not applied to the problem, do not provide a score more than 3 irrespective of the criterion
    4. Scoring Framework:
       - Score 1: Criterion not addressed at all
       - Score 2-3: Vaguely implied but not addressed
       - Score 4-5: Implicitly addressed through solution
       - Score 6-7: Explicitly addressed but not fully explained
       - Score 8-10: Explicitly addressed with clear explanation
    5. Consider the entire chat history when determining if a criterion has been addressed
    6. Do not infer or assume knowledge not demonstrated in the answer
    7. Related subcriteria should be scored consistently with each other
    
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
      eval_distribution: {eval_distribution}
      
    The chat_history is a sequence of question/answer pairs, each pair representing a conversation turn between the interviewer and candidate respectively. Score the recent most candidate answer against each sub-criterion between 1 to 10. Ensure that the structure and length of the subcriteria remain the same and no new subcriterion are added.

    YOU MUST RESPOND IN THE FOLLOWING LIST FORMAT:
    [
        "answer_evaluation",
        "rationale"
    ]
    The answer_evaluation response must be in strict JSON format as given in the example below.
    
    Example:
    [
        {{
            "Subcriterion question": "4",
            "Subcriterion question": "4",
            "Subcriterion question": "2"
        }},
        "rationale"
    ]
    The response should only include the list containing the evaluation and rationale.
    
    Response:
    """
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt
def make_prompt_from_template_wo_rationale():
  eval_prompt_str = """
    You are an expert interviewer with experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity.
    
    EVALUATION GUIDELINES:
    1. Only evaluate and score subcriteria that the candidate has EXPLICITLY addressed in their answers
    2. For any subcriterion that the candidate has not EXPLICITLY addressed, assign a score of 1
    3. If the solution contains best practices and is not applied to the problem, do not provide a score more than 3 irrespective of the criterion
    4. Scoring Framework:
       - Score 1: Criterion not addressed at all
       - Score 2-3: Vaguely implied but not addressed
       - Score 4-5: Implicitly addressed through solution
       - Score 6-7: Explicitly addressed but not fully explained
       - Score 8-10: Explicitly addressed with clear explanation
    5. Consider the entire chat history when determining if a criterion has been addressed
    6. Do not infer or assume knowledge not demonstrated in the answer
    7. Related subcriteria should be scored consistently with each other
    
    Given the following inputs:
      question: {question}
      answer: {answer}
      chat_history: {chat_history}
      subcriteria: {subcriteria}
      eval_distribution: {eval_distribution}
      
    The chat_history is a sequence of question/answer pairs, each pair representing a conversation turn between the interviewer and candidate respectively. Score the recent most candidate answer against each sub-criterion between 1 to 10. Ensure that the structure and length of the subcriteria remain the same and no new subcriterion are added.
    
    The response must be in strict JSON format as given in the example below.
    Example:
    {{
        "Subcriterion question": "4",
        "Subcriterion question": "4",
        "Subcriterion question": "2"
    }}
    Response:
"""
  eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
  return eval_prompt

def make_prompt_from_template_nabiha():
    eval_prompt_str = """
        You are an expert interviwer specialized for evaluating answer for question.
        Given the question answer and chat_history, You must evaluate the answer according to the given subcriteria and give score out of 10.
        The score must be based on the performance of candidate in each subcriteria.
        
        question: {question}
        answer: {answer}
        chat_history: {chat_history}
        subcriteria: {subcriteria}

        You must only give score 10 if subcriteria is completely satisfied, otherwise 1 being the least satisfied in response.
        You must evaluate each parameter and give its response.
        The response must be in dict format like in example.

        Example:
            {{
                "Are the definitions of vowels (e.g., considering both uppercase and lowercase) specified?": "5", 
                "Is it clear whether the input will be a valid string or can it include non-string types?": "10",
                "Are there any restrictions on the characters in the input string?": "3"
            }}

        Response:
      """
    eval_prompt = ChatPromptTemplate.from_template(template=eval_prompt_str)
    return eval_prompt