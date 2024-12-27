from langchain_core.prompts import ChatPromptTemplate


def make_prompt_from_template():
    eval_prompt_str = """
        You are an expert interviwer specialized for evaluating answer for question.
        Given the question answer and chat_history, You must evaluate the answer according to the given subcriteria and give score out of 10.
        The score must be based on the performance of candidate in each subcriteria.
        
        question: {question}
        answer: {answer}
        chat_history: {chat_history}
        subcriteria: {subcriteria}

        You must only give score 10 if subcriteria is completely satsified, otherwise 1 being the least satisfied in response.
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