from langchain_core.prompts import ChatPromptTemplate

def bot_dialogue_prompt_template():
  
  prompt="""
    Given:
    Class: {class}
    Question: {question}
    Follow-up Question (if any): {follow_up_question}
    Candidate Dialogue: {answer}
    Chat History: {chat_history}
    You are an agent who provides responses as per the instructions given below alongside each class while considering the above artifacts as well.

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
  - If class is 'irrelevant': Acknowledge the candidate's response and redirect them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
  - If class is 'interview_inquiry': The response should elegantly answer what the candidate has asked regarding the interview process
  - If class is 'clarification(specific)': The response should elegantly only clarify the specific question asked, without revealing any details or implementation steps about the solution  
  - If class is 'clarification(open)': Professionally decline providing a clarification and encourage the candidate to ask something specific
  - If class is 'request(guidance)': Professionally decline providing a detailed guidance
  - If class is 'request(termination)': Express gratitude for the candidate's participation and confirm the termination of the interview in a professional manner
  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
  - If class is 'disregard': Conclude the interview professionally if its an extremely explicit disregard otherwise respond suitably if its a slight disregard
  - If class is 'uncertainty': Verify if the candidate has some issues
  - If class is 'technical': Generate a contextually appropriate response that maintains the natural flow of the interview while staying focused on the assessment objectives

  You must respond ONLY in this exact format:
  ["class", "response", "rationale"] where 'rationale' is your reasoning for generating the response as such
  
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt

def bot_dialogue_prompt_rationale():
  
  prompt="""
    Given:
    Class: {class}
    Question: {question}
    Follow-up Question (if any): {follow_up_question}
    Candidate Dialogue: {answer}
    Chat History: {chat_history}
    Rationale: {rationale}
    You are an agent who provides responses as per the instructions given below alongside each class while considering the above artifacts as well.

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
  - If class is 'irrelevant': Acknowledge the candidate's response and redirect them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
  - If class is 'clarification(specific)': The response should elegantly only clarify the specific question asked, without revealing any details or implementation steps about the solution  
  - If class is 'clarification(open)': Professionally decline providing a clarification and encourage the candidate to ask something specific
  - If class is 'request(guidance)': Professionally decline providing a detailed guidance
  - If class is 'request(termination)': Express gratitude for the candidate's participation and confirm the termination of the interview in a professional manner
  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
  - If class is 'disregard': Conclude the interview professionally if its an extremely explicit disregard otherwise respond suitably if its a slight disregard
  - If class is 'uncertainty': Verify if the candidate has some issues
  - If class is 'technical': Generate a contextually appropriate response that maintains the natural flow of the interview while staying focused on the assessment objectives

  - If class is 'correct(partial)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.

  - If class is 'incorrect': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'completeness(superficial)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'completeness(comprehensive)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(optimal)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(suboptimal)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(innovative)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(conventional)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(clear)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(unclear)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(verbose)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(concise)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(adaptable)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(rigid)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(hypothetical)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'verification(done)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'verification(not_done)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  You must respond ONLY in this exact format:
  ["class", "response", "rationale"] where 'rationale' is your reasoning for generating the response as such
  """
  
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt
def bot_dialogue_prompt_template_Ritesh():
  
  prompt="""
    Given:
    Class: {class}
    Question: {question}
    Follow-up Question (if any): {follow_up_question}
    Candidate Dialogue: {answer}
    Chat History: {chat_history}
    Rationale: {rationale}
    You are an agent who provides responses as per the instructions given below alongside each class while considering the above artifacts as well.

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
  - If class is 'irrelevant': Acknowledge the candidate's response and redirect them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
  - If class is 'clarification(specific)': The response should elegantly only clarify the specific question asked, without revealing any details or implementation steps about the solution  
  - If class is 'clarification(open)': Professionally decline providing a clarification and encourage the candidate to ask something specific
  - If class is 'request(guidance)': Professionally decline providing a detailed guidance
  - If class is 'request(termination)': Express gratitude for the candidate's participation and confirm the termination of the interview in a professional manner
  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
  - If class is 'disregard': Conclude the interview professionally if its an extremely explicit disregard otherwise respond suitably if its a slight disregard
  - If class is 'uncertainty': Verify if the candidate has some issues
  - If class is 'technical': Generate a contextually appropriate response that maintains the natural flow of the interview while staying focused on the assessment objectives

  - If class is 'correct(partial)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.

  - If class is 'incorrect': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'completeness(superficial)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'completeness(comprehensive)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(optimal)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(suboptimal)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(innovative)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'algorithm(conventional)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(clear)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(unclear)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(verbose)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'clarity(concise)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(adaptable)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(rigid)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'approach(hypothetical)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'verification(done)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  - If class is 'verification(not_done)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
  You must respond ONLY in this exact format:
  ["class", "response", "rationale"] where 'rationale' is your reasoning for generating the response as such
  """
  
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt
def bot_dialogue_prompt_template_v1():
  
  prompt="""
    Given:
    Class: {class}
    Question: {question}
    Follow-up Question (if any): {follow_up_question}
    Candidate Dialogue: {answer}
    Chat History: {chat_history}
    
    You are an agent who provides responses as per the instructions given below alongside each class while considering the above artifacts as well.

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
  - If class is 'irrelevant': Acknowledge the candidate's response and redirect them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
  - If class is 'clarification(specific)': Provide a clear and concise explanation addressing the specific points of confusion the candidate has raised about the question while ensuring no solution details are revealed
  - If class is 'clarification(knowledge_expectation)': The response should directly confirm or deny, set clear expectations, and encourage an attempt at answering.



  - If class is 'clarification(open)': Professionally decline providing a clarification
  - If class is 'request(guidance)': Professionally decline providing a detailed guidance
  - If class is 'request(termination)': Express gratitude for the candidate's participation and confirm the termination of the interview in a professional manner
  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
  - If class is 'uncertainty': Verify if the candidate has some issues
  - If class is 'technical(unclear)': Prompt the candidate to clarify their response
  - If class is 'technical': Generate a contextually appropriate response that maintains the natural flow of the interview while staying focused on the assessment objectives

    You must respond ONLY in this exact format:
    ["class", "response", "rationale"] where 'rationale' is your reasoning for generating the response as such
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt
