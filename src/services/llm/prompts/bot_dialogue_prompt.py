from langchain_core.prompts import ChatPromptTemplate

def bot_dialogue_prompt_template_list():
  
  prompt="""
    Given:
    class: {class}
    tech_question: {tech_question}
    bot_dialogue (if any): {bot_dialogue}
    candidate_dialogue: {candidate_dialogue}
    chat_history: {chat_history}
    rationale: {rationale}
    answer_evaluation: {answer_evaluation}
    
    This prompt contains two groups of non-technical and technical class labels as listed below.

    Among the other arguments received above the prompt receives a class argument.
    Now, you are an agent which matches this class with one of the class labels listed below and provides:
      * Concise response or follow-up question as per the instructions given below alongside each class label    
      * An action_flag variable that helps perform certain operations further in the system based on their value

  NON-TECHNICAL CLASS LABELS:

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
    * Assign action_flag as "Pass"
    
  - If class is 'irrelevant': Provide a concise response pointing out specifically how their answer wasn't addressing the question at hand and conclude with a follow-up question while redirecting them back to the original question, 
    * Assign action_flag as "Pass"

  - If class is 'interview_inquiry': The response should elegantly answer what the candidate has asked regarding the interview process
    * Assign action_flag as "Pass"

  - If class is 'confirmation': Consider the most recent question in the chat history to which the candidate has positively responded.
    Based on the collective question and the positive response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'negation': Consider the most recent question in the chat history to which the candidate has negatively responded.
    Based on the collective question and the negative response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'clarification(open)':
    * If the candidate asks about corner cases and edge cases:
        - Refuse to share these cases
    * Else:
        * If the candidate is asking for an open hint/guidance to solve this problem:
          - Professionally deny sharing any information
        * Else:  
          - Provide a concise response ensuring no implementation or algorithmic details are shared  
    * Assign action_flag as "Pass"

  - If class is 'request(new_question)': Acknowledge the candidate's request and provide a suitable response by confirming whether they are ready for the new question.
    * Assign action_flag as "Pass"

  - If class is 'request(termination)': Pose a clear question to the candidate confirming that they want to end or terminate the interview
    * Assign action_flag as "Pass"

  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
    * Assign action_flag as "Pass"

  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
    * Assign action_flag as "Pass"

  - If class is 'disregard':
    * If the candidate expresses slight disregard:
      - Verify whether the candidate wishes to continue further
    * If the candidate has used inappropriate language:
      - Professionally end the interview with a suitable concluding response
    * Assign action_flag as "Pass"

  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
    * Assign action_flag as "Pass"

  - If class is 'inability': 
    * If the candidate would like clarification on the current question
      - Provide a suitable response in the form of a query
    * If the candidate wants to try a different question
      - Provide a suitable response in the form of a query
    * If the candidate expresses inability citing some other issues
      - Provide a suitable response in the form of a query
    * Assign action_flag as "Pass"
  
  - If class is 'uncertainty': 
    * If the candidate is uncertain about solving the technical problem:
        - Professionally deny sharing any information
    * Else:
        * If the candidate is uncertain about non-technical issues
          - Verify what kind of non-technical issues he has and provide a concise response ensuring no implementation or algorithmic details are shared
    * Assign action_flag as "Pass"

  TECHNICAL CLASS LABELS:
  
  - If class is 'solution': Prepare a very concise follow-up question based on the following instructions:
      1. Based on the answer_evaluation and the subcriteria scores present within, if there are relatively lower scoring subcriteria or in particular if a subcriterion score is equal to 0 then prepare the follow-up question based on such subcriteria
      2. While preparing the follow-up question also keep in mind, the rationale received as an argument in this prompt
      3. In addition, while preparing the follow-up question ensure that a similar question does not exist in the chat_history
    * Assign action_flag as "Pass"
    
  - If class is 'doubt(concept)': Provide a concise follow-up question by also keeping in mind the rationale received as arguments in this prompt
    * Assign action_flag as "Pass"

  - If class is 'doubt(problem)': Provide a concise follow-up question by also keeping in mind the rationale received as arguments in this prompt
    * Assign action_flag as "Pass"

  You must respond ONLY in this exact list format:
  ["class", "response", "rationale", "subcriterion", "action_flag"]

  Requirements:
  1. List must contain exactly 5 elements
  2. If any element is not applicable, use an empty string "" (not None)
  3. Elements are defined as:
    - class: Classification or category
    - response: Your generated response
    - rationale: Your reasoning for generating the response
    - subcriterion: The subcriterion question from answer evaluation (if none exists, use "")
    - action_flag: The action to be initiated in the system
  4. Your generated response should be in meaningful chunks so that it could be passed to the next text to speech layer
  The list format must be preserved exactly as shown above.
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt

def bot_dialogue_prompt_template():
  
  prompt="""
    Given:
    class: {class}
    tech_question: {tech_question}
    bot_dialogue (if any): {bot_dialogue}
    candidate_dialogue: {candidate_dialogue}
    chat_history: {chat_history}
    rationale: {rationale}
    answer_evaluation: {answer_evaluation}
    
    This prompt contains two groups of non-technical and technical class labels as listed below.

    Among the other arguments received above the prompt receives a class argument.
    Now, you are an agent which matches this class with one of the class labels listed below and provides:
      * Concise response or follow-up question as per the instructions given below alongside each class label    
      * An action_flag variable that helps perform certain operations further in the system based on their value

    You must respond ONLY in this exact dictionary format:
    {{
    "class": class_label,
    "response": response,
    "rationale": rationale,
    "subcriterion": subcriterion,
    "action_flag": action_flag
    }}

    Requirements:
    1. Dictionary must contain exactly 5 key-value pairs
    2. Keys are defined as:
      - class: Classification or category
      - response: Your generated response
      - rationale: Your reasoning for generating the response
      - subcriterion: The subcriterion question from answer evaluation from which you formulated the follow-up question
      - action_flag: The action to be initiated in the system

  NON-TECHNICAL CLASS LABELS:

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
    * Assign action_flag as "Pass"
    
  - If class is 'irrelevant': Provide a concise response pointing out specifically how their answer wasn't addressing the question at hand and conclude with a follow-up question while redirecting them back to the original question, 
    * Assign action_flag as "Pass"

  - If class is 'interview_inquiry': The response should elegantly answer what the candidate has asked regarding the interview process
    * Assign action_flag as "Pass"

  - If class is 'confirmation': Consider the most recent question in the chat history to which the candidate has positively responded.
    Based on the collective question and the positive response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'negation': Consider the most recent question in the chat history to which the candidate has negatively responded.
    Based on the collective question and the negative response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'clarification(open)':
    * If the candidate asks about corner cases and edge cases:
        - Refuse to share these cases
    * Else:
        * If the candidate is asking for an open hint/guidance to solve this problem:
          - Professionally deny sharing any information
        * Else:  
          - Provide a concise response ensuring no implementation or algorithmic details are shared  
    * Assign action_flag as "Pass"

  - If class is 'request(new_question)': Acknowledge the candidate's request and provide a suitable response by confirming whether they are ready for the new question.
    * Assign action_flag as "Pass"

  - If class is 'request(termination)': Pose a clear question to the candidate confirming that they want to end or terminate the interview
    * Assign action_flag as "Pass"

  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
    * Assign action_flag as "Pass"

  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
    * Assign action_flag as "Pass"

  - If class is 'disregard':
    * If the candidate expresses slight disregard:
      - Verify whether the candidate wishes to continue further
    * If the candidate has used inappropriate language:
      - Professionally end the interview with a suitable concluding response
    * Assign action_flag as "Pass"

  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
    * Assign action_flag as "Pass"

  - If class is 'inability': 
    * If the candidate would like clarification on the current question
      - Provide a suitable response in the form of a query
    * If the candidate wants to try a different question
      - Provide a suitable response in the form of a query
    * If the candidate expresses inability citing some other issues
      - Provide a suitable response in the form of a query
    * Assign action_flag as "Pass"
  
  - If class is 'uncertainty': 
    * If the candidate is uncertain about solving the technical problem:
        - Professionally deny sharing any information
    * Else:
        * If the candidate is uncertain about non-technical issues
          - Verify what kind of non-technical issues he has and provide a concise response ensuring no implementation or algorithmic details are shared
    * Assign action_flag as "Pass"

  TECHNICAL CLASS LABELS:
  
  - If class is 'solution': Prepare a very concise follow-up question based on the following instructions:
      1. Based on the answer_evaluation and the subcriteria scores present within, if there are relatively lower scoring subcriteria or in particular if a subcriterion score is equal to 0 then prepare the follow-up question based on such subcriteria
      2. While preparing the follow-up question also keep in mind, the rationale received as an argument in this prompt
      3. In addition, while preparing the follow-up question ensure that a similar question does not exist in the chat_history
    * Assign action_flag as "Pass"
    
  - If class is 'doubt(concept)': Provide a concise follow-up question by also keeping in mind the rationale received as arguments in this prompt
    * Assign action_flag as "Pass"

  - If class is 'doubt(problem)': Provide a concise follow-up question by also keeping in mind the rationale received as arguments in this prompt
    * Assign action_flag as "Pass"
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt

def bot_dialogue_prompt_template_verbose():
  
  prompt="""
    Given:
    class: {class}
    tech_question: {tech_question}
    bot_dialogue (if any): {bot_dialogue}
    candidate_dialogue: {candidate_dialogue}
    chat_history: {chat_history}
    rationale: {rationale}
    answer_evaluation: {answer_evaluation}
    
    You are an agent who provides:
      * Concise response or follow-up questions as per the instructions given below alongside each class label    
      * An action_flag variable that helps perform certain operations further in the system based on their value
    
    The class labels for a candidate_dialogue have been further grouped into non-technical and technical class labels

    In particular, for the technical group of class labels consider the answer_evaluation payload received above. Please ensure that responses are in the form of concise questions directed towards the candidate. Prepare the questions with the following guidelines in mind.
    1. If the candidate_dialogue has not been able to answer the bot_dialogue completely then prepare the response based on the finer instructions as mentioned below each alongside each class label
    2. Based on the answer_evaluation and the subcriteria scores present within, if there are relatively lower scoring subcriteria or in particular if a subcriterion score is equal to 0 then prepare the question based on such subcriteria
    
  NON-TECHNICAL CLASS LABELS:

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
    * Assign action_flag as "Pass"
    
  - If class is 'irrelevant': Acknowledge the candidate's response and provide a suitable response redirecting them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
    * Assign action_flag as "Pass"

  - If class is 'interview_inquiry': The response should elegantly answer what the candidate has asked regarding the interview process
    * Assign action_flag as "Pass"

  - If class is 'confirmation': Consider the most recent question in the chat history to which the candidate has positively responded.
    Based on the collective question and the positive response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'negation': Consider the most recent question in the chat history to which the candidate has negatively responded.
    Based on the collective question and the negative response, reason about the intention of the candidate_dialogue.
    * If the intention seems to be close to one of the following categories then, follow the respective instructions given along side:
      - "terminate_interview_confirmation": Respond with : "Thank you for your participation!", assign action_flag as "terminate_interview_confirmation" 
    * Else:
      - Based on the intention identified above provide a concise response ensuring no implementation or algorithmic details are shared, assign action_flag as "Pass"

  - If class is 'clarification(open)':
    * If the candidate asks about corner cases and edge cases:
        - Refuse to share these cases
    * Else:
        * If the candidate is asking for an open hint/guidance to solve this problem:
          - Professionally deny sharing any information
        * Else:  
          - Provide a concise response ensuring no implementation or algorithmic details are shared  
    * Assign action_flag as "Pass"

  - If class is 'request(new_question)': Acknowledge the candidate's request and provide a suitable response by confirming whether they are ready for the new question.
    * Assign action_flag as "Pass"

  - If class is 'request(termination)': Pose a clear question to the candidate confirming that they want to end or terminate the interview
    * Assign action_flag as "Pass"

  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
    * Assign action_flag as "Pass"

  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
    * Assign action_flag as "Pass"

  - If class is 'disregard':
    * If the candidate expresses slight disregard:
      - Verify whether the candidate wishes to continue further
    * If the candidate has used inappropriate language:
      - Professionally end the interview with a suitable concluding response
    * Assign action_flag as "Pass"

  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
    * Assign action_flag as "Pass"

  - If class is 'inability': 
    * If the candidate would like clarification on the current question
      - Provide a suitable response in the form of a query
    * If the candidate wants to try a different question
      - Provide a suitable response in the form of a query
    * If the candidate expresses inability citing some other issues
      - Provide a suitable response in the form of a query
    * Assign action_flag as "Pass"
  
  - If class is 'uncertainty': 
    * If the candidate asks about uncertain about solving the technical problem:
        - Professionally deny sharing any information
    * Else:
        * If the candidate is uncertain about non-technical issues
          - Verify what kind of non-technical issues he has and provide a concise response ensuring no implementation or algorithmic details are shared
    * Assign action_flag as "Pass"

  TECHNICAL CLASS LABELS:
  
  - If class is 'solution': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
    * Assign action_flag as "Pass"
    
  - If class is 'doubt(concept)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
    * Assign action_flag as "Pass"

  - If class is 'doubt(problem)': Write concise response by considering the rationale given above and conclude the response with a follow-up question.
    * Assign action_flag as "Pass"

  You must respond ONLY in this exact list format:
  ["class", "response", "rationale", "subcriterion", "action_flag"]

  Requirements:
  1. List must contain exactly 5 elements
  2. If any element is not applicable, use an empty string "" (not None)
  3. Elements are defined as:
    - class: Classification or category
    - response: Your generated response
    - rationale: Your reasoning for generating the response
    - subcriterion: The subcriterion question from answer evaluation (if none exists, use "")
    - action_flag: The action to be initiated in the system
  4. Your generated response should be in meaningful chunks so that it could be passed to the next text to speech layer
  The list format must be preserved exactly as shown above.
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt

      # - Professionally end the interview with a suitable concluding response
def bot_dialogue_prompt_template_current():
  
  prompt="""
    Given:
    Class: {class}
    Question: {question}
    Follow-up Question (if any): {follow_up_question}
    Candidate Dialogue: {answer}
    Chat History: {chat_history}
    Rationale: {rationale}
    Answer Evaluation: {answer_evaluation}
    
    The following contains class labels for a dialogue utterance grouped into non-technical and technical categories as shown below.
    
    You are an agent who provides concise responses as per the instructions given below alongside each class while considering the above artifacts as well.     

    In particular for the technical group of class labels consider the answer_evaluation payload received above. Please ensure that responses are in the form of concise questions directed towards the candidate. Prepare the questions with the following guidelines in mind.
    1. If the utterance has not been able to answer the previous question completely then prepare the response based on the finer instructions as mentioned below each alongside each class label
    2. Based on the answer evaluation and the subcriteria scores present within, if there are relatively lower scoring subcriteria or in particular if a subcriterion score is equal to 1 then prepare the question based on such subcriteria and please include the subcriteria in the following format.
    
  NON-TECHNICAL GROUP:

  - If class is 'illegible': Politely ask the candidate to rephrase their response as it appears unclear or contains non-standard language
  - If class is 'irrelevant': Acknowledge the candidate's response and redirect them back to the original question, pointing out specifically how their answer wasn't addressing the question at hand
  - If class is 'interview_inquiry': The response should elegantly answer what the candidate has asked regarding the interview process
  - If class is 'clarification(specific)':
      * If the candidate's clarification is about corner cases or edge cases:
          - Professionally deny sharing these cases
      * Else:
          - Provide a concise clarification for the specific question asked
          - Ensure no implementation or algorithmic details are shared
  - If class is 'clarification(open)':
    * If the candidate asks about corner cases and edge cases:
        - Refuse to share these cases
    * Else:
        * If the candidate is asking for an open hint/guidance to solve this problem
          - Professionally deny sharing any information
        * Else  
          - Provide a concise response ensuring no implementation or algorithmic details are shared  
  - If class is 'request(termination)':
    * If the candidate has explicitly asked to end the interview:
      - Professionally end the interview with a suitable concluding response
  - If class is 'request(proceed)': Give an encouraging confirmation for the candidate to proceed with their approach, maintaining a supportive tone
  - If class is 'request(break)': Grant a specific break duration (not exceeding 1 minute) and clearly state when to resume the interview
  - If class is 'illegitimate': Professionally decline the illegitimate request while maintaining interview decorum, and redirect the conversation back to the appropriate topic
  according to the intention conveyed
  - If class is 'disregard':
    * If the candidate expresses slight disregard:
      - Verify whether the candidate wishes to continue further
    * If the candidate has used inappropriate language:
      - Professionally end the interview with a suitable concluding response
  - If class is 'uncertainty': 
    * If the candidate asks about uncertain about solving the technical problem:
        - Professionally deny sharing any information
    * Else:
        * If the candidate is uncertain about non-technical issues
          - Verify what kind of non-technical issues he has and provide a concise response ensuring no implementation or algorithmic details are shared

  TECHNICAL GROUP:
          
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
  ["class", "response", "rationale, "subcriteria"] where 'rationale' is your reasoning for generating the response as such
  where subcriteria is the subcriterion question present from the answer evaluation
  """
  policy_violation_prompt=ChatPromptTemplate.from_template(template=prompt)
  return policy_violation_prompt
