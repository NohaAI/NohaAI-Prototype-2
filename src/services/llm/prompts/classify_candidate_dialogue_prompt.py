from langchain_core.prompts import ChatPromptTemplate
 
# TO-DO: self-correction/apology can be added

def classify_candidate_dialogue_prompt_template_dated_2_3_2025():
  prompt="""
  
  You are emulating a dialogue act classifier. Your task is to label the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  Question: {question}
  Candidate Dialogue: {answer}
  Interim Chat History: {interim_chat_history}

  'class' must be one of:
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - clarification(open) - Candidate asks for a very open-ended clarification
  - request(guidance) - Candidate asks for a detailed guidance or a stepwise explanation
  - request(termination) - Candidate explicitly requests to end the interview
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview.
  - illegitimate - Candidate is making illegitimate requests or statement 
  - uncertainty - Candidate utters a response which expresses uncertainty
  - technical - Candidate dialogue that do no classify in any of the above classes 

  'classification logic' for determining the appropriate class:
    *Take in account interim chat history while classifying

  - Classify the dialogue as 'technical' when the following criteria are met:
    * Contains non-dictionary words or random character sequences
    * Has grammatically incorrect sentence structures that make meaning unclear
    * Contains excessive typos or transcription errors

  - Classify the dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  -Classify the dialogue as 'interview_inquiry' when the following criteria are met:
    * The candidate asks questions related to the interview process, such as its duration, structure, or status.
    * Examples include questions like "Are we done with the interview?", "What is the duration of the interview?", "How many questions are there in this interview?", etc.
    * These inquiries are not about the specific questions being asked but focus on the overall interview process.
  
  - Classify the dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specfic terms  listed in the question
    * The question is framed to verify the interview's scope and expectations
    * Candidate has asked for a clarification about aspects that are related to the problem or are related to its possible solution
   
  - Classify the dialogue as 'clarification(open)' when the following criteria are met:  
    * When the clarification is open-ended

  - Classify the dialogue as 'request(guidance)' when the following criteria are met:
    * The dialogue represents requests for detailed guidance or a stepwise explanation or response to the problem  
        
  - Classify the dialogue as 'request(termination)' when the following criteria are met:
    * The candidate explicitly states they want to exit the interview.
    * The candidate cites an emergency requiring an immediate exit.
    * Do not classify as 'request(termination)' if the candidate merely expresses unwillingness or a general desire not to continue (e.g., "I don't want to give this interview") without citing an emergency or directly stating they want to exit. These should be classified as disregard.
    
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * Any open-ended request for guidance must not be considered
    * Dialogue represents that the candidate is thinking aloud
        
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language 
    * The candidate expresses disinterest or unwillingness to continue the interview without using polite or neutral language 
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - For class 'uncertainty' here are few positive examples for this class:
    Positive: 
      "I don't know how to solve this problem"
      "I don't know what to do now"

  You must respond ONLY in this exact format:
  ["class", "rationale"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt
def classify_candidate_dialogue_prompt_template():
  prompt="""
  
  You are emulating a dialogue act classifier. Your task is to label the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  Question: {question}
  Candidate Dialogue: {answer}
  Interim Chat History: {interim_chat_history}

  'class' must be one of:
  - technical - Candidate has attempted to solve this question 
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - request(guidance) - Candidate asks for a detailed guidance or a stepwise explanation
  - request(termination) - Candidate explicitly requests to end the interview 
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview
  - illegitimate - Candidate is making illegitimate requests or statement 
  - uncertainty - Candidate utters a response which expresses uncertainty

  'classification logic' for determining the appropriate class:
    * Take in account interim chat history while classifying

  - Classify the dialogue as 'technical' when the following criteria are met:
   * The candidate has made an attempt to answer the problem

  - Classify the dialogue as 'illegible' when the following criteria are met:
    * Contains non-dictionary words or random character sequences
    * Has grammatically incorrect sentence structures that make meaning unclear
    * Contains excessive typos or transcription errors

  - Classify the dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  -Classify the dialogue as 'interview_inquiry' when the following criteria are met:
    * The candidate asks questions related to the interview process, such as its duration, structure, or status.
    * Examples include questions like "Are we done with the interview?", "What is the duration of the interview?", "How many questions are there in this interview?", etc.
    * These inquiries are not about the specific questions being asked but focus on the overall interview process.

  - Classify the dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specific terms  listed in the question
    * The question is framed to verify the interview's scope and expectations
    
  - Classify the dialogue as 'request(guidance)' when the following criteria are met:
    * The dialogue represents requests for detailed guidance or a stepwise explanation or response to the problem  
        
  - Classify the dialogue as 'request(termination)' when the following criteria are met:
    * The candidate explicitly states they want to exit the interview.
    * The candidate cites an emergency requiring an immediate exit.
    * Do not classify as 'request(termination)' if the candidate merely expresses unwillingness or a general desire not to continue (e.g., "I don't want to give this interview") without citing an emergency or directly stating they want to exit. These should be classified as disregard.
  
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * Any open-ended request for guidance must not be considered
    * Dialogue represents that the candidate is thinking aloud
        
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language 
    * The candidate expresses disinterest or unwillingness to continue the interview without using polite or neutral language 
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - Classify the dialogue as 'uncertainty' when the following criteria are met:
    * The candidate expresses uncertainty about the next steps or what action to take
    * The candidate explicitly states they do not know how to proceed or solve a problem

  You must respond ONLY in this exact format:
  ["class", "rationale"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt
def classify_candidate_dialogue_prompt_template_current():
  prompt="""
  
  You are emulating a dialogue act classifier. Your task is to label the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  Question: {question}
  Candidate Dialogue: {answer}
  Interim Chat History: {interim_chat_history}

  'class' must be one of:
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - clarification(open) - Candidate asks for a very open-ended clarification
  - request(guidance) - Candidate asks for a detailed guidance or a stepwise explanation
  - request(termination) - Candidate explicitly requests to end the interview
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview
  - illegitimate - Candidate is making illegitimate requests or statement 
  - uncertainty - Candidate utters a response which expresses uncertainty
  - technical - Candidate dialogue that do no classify in any of the above classes 

  'classification logic' for determining the appropriate class:
    *Take in account interim chat history while classifying

  - Classify the dialogue as 'illegible' when the following criteria are met:
    * Contains non-dictionary words or random character sequences
    * Has grammatically incorrect sentence structures that make meaning unclear
    * Contains excessive typos or transcription errors

  - Classify the dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  -Classify the dialogue as 'interview_inquiry' when the following criteria are met:
    * The candidate asks questions related to the interview process, such as its duration, structure, or status.
    * Examples include questions like "Are we done with the interview?", "What is the duration of the interview?", "How many questions are there in this interview?", etc.
    * These inquiries are not about the specific questions being asked but focus on the overall interview process.

  - Classify the dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specfic terms  listed in the question
    * The question is framed to verify the interview's scope and expectations
    * Candidate has asked for a clarification about aspects that are related to the problem or are related to its possible solution
   
  - Classify the dialogue as 'clarification(open)' when the following criteria are met:  
    * When the clarification is open-ended

  - Classify the dialogue as 'request(guidance)' when the following criteria are met:
    * The dialogue represents requests for detailed guidance or a stepwise explanation or response to the problem  
        
  - Classify the dialogue as 'request(termination)' when the following criteria are met:
    * The candidate explicitly states they want to exit the interview.
    * The candidate cites an emergency requiring an immediate exit.
    * Do not classify as 'request(termination)' if the candidate merely expresses unwillingness or a general desire not to continue (e.g., "I don't want to give this interview") without citing an emergency or directly stating they want to exit. These should be classified as disregard.
    
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * Any open-ended request for guidance must not be considered
    * Dialogue represents that the candidate is thinking aloud
        
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language 
    * The candidate expresses disinterest or unwillingness to continue the interview without using polite or neutral language 
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - For class 'uncertainty' here are few positive examples for this class:
    Positive: 
      "I don't know how to solve this problem"
      "I don't know what to do now"

  - Classify the dialogue as 'technical' when the following criteria are met:
    * General statements about problem-solving progress
    * Expressions of difficulty without specific questions
    * Valid responses that don't fit other categories

  You must respond ONLY in this exact format:
  ["class", "rationale"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt
def classify_candidate_dialogue_prompt_template_v1():
  prompt="""
  
  You are emulating a dialogue act classifier. Your task is to label the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  Question: {question}
  Candidate Dialogue: {answer}
  Interim Chat History: {interim_chat_history}

  'class' must be one of:
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - clarification(knowledge_expectation) -  A candidate asks if specific knowledge is required. 
  - clarification(specific) - Candidate asks for a very specific clarification
  - clarification(open) - Candidate asks for a very open ended clarification
  - request(guidance) - Candidate asks for a detailed guidance or a stepwise explanation
  - request(termination) - Candidate wants to exit the interview
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - illegitimate - Candidate is making illegitimate requests or statement 
  - uncertainty - Candidate utters a response which expresses uncertainty
  - technical(unclear) - Candidate utters a response which lacks clarity in relation to the problem
  - technical - Candidate dialogue that do no classify in any of the above classes 

  'classification logic' for determining the appropriate class:
    *Take in account interim chat history while classifying

  - Classify the dialogue as 'illegible' when the following criteria are met:
    * Contains non-dictionary words or random character sequences
    * Has grammatically incorrect sentence structures that make meaning unclear
    * Contains excessive typos or transcription errors

  - Classify the dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  - For class 'clarification(specific)' here are a few positive examples for this class:
    Positive:
      "Can I assume that the array is non-empty?"
      "Can I assume the array contains negative integers?

  - Classify the dialogue as 'clarification(knowledge_expectation)' when the following criteria are met:
    * The candidate explicitly asks if certain knowledge (e.g., data structures, recursion, system design) is necessary.
    * The question is framed to verify the interview’s scope and expectations.
    * The ideal response should clarify knowledge requirements rather than probe for concerns or deflect.
  
  - For class 'clarification(open)' here are a few positive examples for this class:
    Positive:
      "What can I assume about this problem?"
      "Please provide some guidance"

  - Classify the dialogue as 'request(guidance)' when the following criteria are met:
    * The dialogue represents requests for detailed guidance or a stepwise explanation or response to the problem  
        
  - Classify the dialogue as 'termination' when the following criteria are met:
    * Clear statements about wanting to end the interview
    * Mentions of emergency situations requiring immediate exit
    * Formal requests to terminate the interview process
    
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * Any open-ended request for guidance must not be considered
    * Dialogue represents that the candidate is thinking aloud
        
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - For class 'uncertainty' here are few positive examples for this class:
    Positive: 
      "I don't know how to solve this problem"
      "I don't know what to do now"

  - Classify the dialogue as 'technical(unclear)' when the following criteria are met:
    * The dialogue appears to be technical however lacks clarity in relation to the problem

  - Classify the dialogue as 'technical' when the following criteria are met:
    * General statements about problem-solving progress
    * Expressions of difficulty without specific questions
    * Valid responses that don't fit other categories

  You must respond ONLY in this exact format:
  ["class", "rationale"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt