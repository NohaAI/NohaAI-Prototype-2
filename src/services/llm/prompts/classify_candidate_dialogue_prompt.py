from langchain_core.prompts import ChatPromptTemplate
 
# TODO: self-correction/apology can be added

def classify_candidate_dialogue_prompt_template():
  prompt="""
  
  You are an agent and your task is to classify the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such. Ensure that you classify the candidate_dialogue with only the labels listed below and that no new label is created.

  Given:
  bot_dialogue: {bot_dialogue}
  candidate_dialogue: {candidate_dialogue}
  chat_history: {chat_history}
  distilled_candidate_dialogue: {distilled_candidate_dialogue}
  
  Before beginning to classify the candidate_dialogue please normalize the candidate_dialogue text as follows : 
    * For confimatory responses like "yes", "no" etc. do not make any changes   
    * For other kinds of texts summarize the candidate dialogue 
    * Also make grammatical corrections (including typos, punctuations) to candidate_dialogue  
  Assign the normalized text to it "distilled_candidate_dialogue".  
                   
  The following is the list of classes alongwith their definitions
  
  When classifying the candidate_dialogue the 'class' must be one of:
  - technical - Candidate has attempted to solve this question 
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - clarification(open) - Candidate asks a generic/non-specific expecting detailed guidance or a stepwise explanation
  - confirmation - Candidate expresses his willingness in the form of confirmatory response
  - negation - Candidate expresses his unwillingness in the form of negative response
  - request(new_question) - Candidate explicitly requests for a new question
  - request(termination) - Candidate explicitly requests to end the interview 
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview
  - illegitimate - Candidate is making illegitimate requests or statement 
  - inability - Candidate shows inability
  - uncertainty - Candidate utters a response which expresses uncertainty

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

  -Classify the dialogue as 'confirmation' when the following criteria are met:
    * Candidate expresses his willingness in the form of confirmatory responses 
    * Examples include 'Yes', 'Yeah', 'Sure', 'Okay', 'Alright', or similar confirmatory verbose paraphrases

  -Classify the dialogue as 'negation' when the following criteria are met:
    * Candidate expresses his reluctance in the form of negative responses 
    * Examples include 'No', 'Nope', 'Not at all', 'Never', or similar verbose paraphrases    

  - Classify the dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specific terms listed in the question
    * The question is framed to verify the interview's scope and expectations
    
  - Classify the dialogue as 'clarification(open)' when the following criteria are met:
    * The dialogue represents a generic/non-specific request expecting detailed guidance or a stepwise explanation  
        
  - Classify the dialogue as 'request(new_question)' when the following criteria are met:
    * The candidate explicitly states that they want alternate question.

  - Classify the dialogue as 'request(termination)' when the following criteria are met:
    * Refer to the chat_history and ensure that this is a initial request for termination and not a confirmation request
  
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * The candidate expresses a direct intention to proceed without any sign of doubt or uncertainty.
  
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language  
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - Classify the dialogue as 'inability' when the following criteria are met:
    * Candidate shows inability to solve the problem  

  - Classify the dialogue as 'uncertainty' when the following criteria are met:
    * The candidate expresses uncertainty about the next steps or what action to take
    * The candidate explicitly states they do not know how to proceed or solve a problem

  You must respond ONLY in this exact format:
  ["class", "rationale", "distilled_candidate_dialogue"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt

def classify_candidate_dialogue_prompt_template_prod():
  prompt="""
  
  You are emulating a dialogue act classifier. Your task is to label the candidate's dialogue into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  bot_dialogue: {bot_dialogue}
  candidate_dialogue: {candidate_dialogue}
  chat_history: {chat_history}

  Summarize candidate_dialogue and make grammatical corrections (including typos, punctuations) to it and then assign it to "distilled_candidate_dialogue".
  'class' must be one of:
  - technical - Candidate has attempted to solve this question 
  - illegible - Possibly some gibberish output or non-standard words coming from STT
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - clarification(open) - Candidate asks a generic/non-specific expecting detailed guidance or a stepwise explanation
  - confirmation - Candidate expresses his willingness in the form of confirmatory response
  - negation - Candidate expresses his unwillingness in the form of negative response
  - request(new_question) - Candidate explicitly requests for a new question
  - request(termination) - Candidate explicitly requests to end the interview 
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview
  - illegitimate - Candidate is making illegitimate requests or statement 
  - inability - Candidate shows inability
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

  -Classify the dialogue as 'confirmation' when the following criteria are met:
    * Candidate expresses his willingness in the form of confirmatory responses 
    * Examples include 'Yes', 'Yeah', 'Sure', 'Okay', 'Alright', or similar confirmatory verbose paraphrases

  -Classify the dialogue as 'negation' when the following criteria are met:
    * Candidate expresses his unwillingness in the form of negative responses 
    * Examples include 'No', 'Nope', 'Not at all', 'Never', or similar verbose paraphrases    

  - Classify the dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specific terms listed in the question
    * The question is framed to verify the interview's scope and expectations
    
  - Classify the dialogue as 'clarification(open)' when the following criteria are met:
    * The dialogue represents a generic/non-specific request expecting detailed guidance or a stepwise explanation  
        
  - Classify the dialogue as 'request(alternate_question)' when the following criteria are met:
    * The candidate explicitly states that they want alternate question.

  - Classify the dialogue as 'request(termination)' when the following criteria are met:
    * The candidate explicitly states they want to exit the interview.
    * The candidate cites an emergency requiring an immediate exit.
  
  - Classify the dialogue as 'request(proceed)' when the following criteria are met:
    * The candidate expresses a direct intention to proceed without any sign of doubt or uncertainty.
  
  - Classify the dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language  
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - Classify the dialogue as 'inability' when the following criteria are met:
    *   

  - Classify the dialogue as 'uncertainty' when the following criteria are met:
    * The candidate expresses uncertainty about the next steps or what action to take
    * The candidate explicitly states they do not know how to proceed or solve a problem

  You must respond ONLY in this exact format:
  ["class", "rationale","distilled_candidate_dialogue"] where 'rationale' is your reasoning for classifying it as such
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt

