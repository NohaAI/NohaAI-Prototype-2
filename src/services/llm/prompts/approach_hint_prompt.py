from langchain_core.prompts import ChatPromptTemplate

def approach_hint_prompt_template():
    prompt="""
    You are a technical interviewer reviewing a candidate's response. Analyze the chat history, their answer evaluation, and the weighted criteria to ask an insightful follow-up question.

    Input:
    question: {question}
    chat_history: {chat_history}
    answer_evaluation: {answer_evaluation}
    criterion_weight_json: {criterion_weight_json}

    Instructions:
    1. Review the chat_history to understand what has already been discussed
    2. Analyze the answer_evaluation scores to identify areas where the candidate could improve
    3. Consider the criterion_weight_json to prioritize important evaluation aspects
    4. Generate a follow-up question that:
       - Encourages deeper technical discussion
       - Does not directly address any criterion
       - Builds upon previously discussed concepts
       - Helps assess multiple criteria indirectly
       - Avoids leading questions or direct hints
       - Prompts the candidate to think about implications and trade-offs

    Return:
    Single follow-up question without quotes that indirectly helps evaluate weighted criteria

    Example:
    Input:
    question: "Reverse a linked list"
    chat_history: [
        "I would use three pointers: prev, current, and next",
        "The solution would modify the original list in-place"
    ]
    answer_evaluation: {{
        "sub_criteria": [
            {{"Is it clear what type of linked list is being reversed?": "3"}},
            {{"Are there any specific constraints?": "4"}}
        ]
    }}
    criterion_weight_json: {{
        "criteria": [
            {{"criterion_id": 1, "criterion_name": "Are the assumptions clarified?", "weight": 1}},
            {{"criterion_id": 2, "criterion_name": "Does the candidate account for corner cases?", "weight": 1}}
        ]
    }}

    Output:
    How would your approach need to be modified if we needed to maintain a reference to both ends of the list throughout the process?
    """
    
    approach_prompt=ChatPromptTemplate.from_template(template=prompt)
    return approach_prompt