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




def make_prompt_from_template():
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