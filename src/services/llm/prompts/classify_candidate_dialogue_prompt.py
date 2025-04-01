from langchain_core.prompts import ChatPromptTemplate
 
# TODO: self-correction/apology can be added

def classify_candidate_dialogue_prompt_template():
  prompt="""
      You are an agent and your task is to classify the candidate's response into different classes as defined below and explain the rationale for classifying them as such. Ensure that you classify the response with only the labels listed below and that no new label is created.

      ### **Given Inputs:**
      - **bot_dialogue**: {bot_dialogue}  
      - **candidate_dialogue**: {candidate_dialogue}  
      - **chat_history**: {chat_history}  
      - **distilled_candidate_dialogue**: {distilled_candidate_dialogue}  

      ---

      ### **Preprocessing Steps (Before Classification)**
      Before beginning to classify the **candidate_dialogue**, apply the following transformations:  
      1. **Confirmatory Responses:**  
        - If candidate_dialogue contains simple confirmations like "yes", "no", "sure," assign it **directly** to distilled_candidate_dialogue without modification.  

      2. **Other Responses:**  
        - **Summarize the response** while preserving its meaning and assign the summarized text to distilled_candidate_dialogue.  

      3. **Grammar & Typo Corrections:**  
        - **Fix grammatical errors, typos, and punctuation** while ensuring clarity.  
        - **The corrected version is assigned to distilled_candidate_dialogue.**  

      ---

      ## **Classification Categories**
      🚨 **Important:**  
      - **Only use distilled_candidate_dialogue for classification.**  
      - **If you classify based on candidate_dialogue instead of distilled_candidate_dialogue, you will be penalized.**  
      - **Choose exactly ONE category per response.**  

      Each response must be classified as **one and only one** of the following:  

      ### **1. technical**
      📌 **When to classify:**  
      - The candidate has **made an attempt to answer the problem**, regardless of correctness.  
      - **Minor grammatical fixes do not affect classification.**  

      ✅ **Example:**  
      - Candidate: *"The corner keys I can think of is it can be a duplicate value."*  
      - After correction: *"The corner cases I can think of are duplicate values."*  
      - ✅ **Classify as 'technical'** because the candidate is attempting to answer.  

      ---

      ### **2. illegible**
      📌 **When to classify:**  
      A response is **illegible** **ONLY** if the **final distilled_candidate_dialogue** meets **at least one** of these conditions:  

      1. **Gibberish or Nonsensical Content:**  
        - The response consists **mostly** of random characters, non-standard words, or incoherent phrases.  
        - More than **70 percent of the words are unrecognizable or meaningless**.  

      2. **Severe Structural Incoherence:**  
        - The sentence lacks **any logical flow** or **any readable subject-verb relationship**.  
        - The meaning **cannot be derived**, even with correction attempts.  

      3. **Completely Unclear Meaning:**  
        - After fixing minor typos and grammar issues, the **core intent is still lost**.  

      🚨 **Important:**  
      - If the meaning is **recoverable after correction**, classify as something else (not ‘illegible’).  

      ---

      ### **3. irrelevant**
      📌 **When to classify:**  
      - The response **does not** answer the active question.  
      - The candidate discusses **something unrelated** to problem-solving.  
      - The response **references the main question when a follow-up should be answered.**  

      ---

      ### **4. interview_inquiry**
      📌 **When to classify:**  
      - The candidate asks about the **interview process** (e.g., duration, number of questions, format).  
      - **Not** about the specific problem itself.  

      ✅ **Example:**  
      - *"How many questions are in this interview?"* → **interview_inquiry**  

      ---

      ### **5. confirmation**
      📌 **When to classify:**  
      - The candidate expresses willingness with **confirmatory responses**.  

      ✅ **Examples:**  
      - *"Yes."*, *"Sure."*, *"Alright."* → **confirmation**  

      ---

      ### **6. negation**
      📌 **When to classify:**  
      - The candidate expresses **reluctance** or **negative responses**.  

      ✅ **Examples:**  
      - *"No."*, *"Not really."*, *"I don’t think so."* → **negation**  

      ---

      ### **7. clarification(specific)**
      📌 **When to classify:**  
      - The candidate asks if **specific knowledge** (e.g., recursion, graphs) is needed.  
      - The candidate **asks for definitions of technical terms**.  

      ✅ **Example:**  
      - *"Do I need to use recursion here?"* → **clarification(specific)**  

      ---

      ### **8. clarification(open)**
      📌 **When to classify:**  
      - The candidate asks for a **general explanation** or **stepwise guidance**.  

      ✅ **Example:**  
      - *"Can you explain how to approach this?"* → **clarification(open)**  

      ---

      ### **9. request(new_question)**
      📌 **When to classify:**  
      - The candidate **explicitly asks for a different question**.  

      ✅ **Example:**  
      - *"Can I get another question?"* → **request(new_question)**  

      ---

      ### **10. request(termination)**
      📌 **When to classify:**  
      - The candidate **initially requests** to end the interview.  
      - **Check chat_history** to ensure it’s the first termination request.  

      ---

      ### **11. request(proceed)**
      📌 **When to classify:**  
      - The candidate requests to continue **without hesitation**.  

      ✅ **Example:**  
      - *"Can I proceed?"* → **request(proceed)**  

      ---

      ### **12. request(break)**
      📌 **When to classify:**  
      - The candidate **explicitly requests a break**.  

      ---

      ### **13. disregard**
      📌 **When to classify:**  
      - The candidate **uses offensive or unprofessional language**.  

      ---

      ### **14. illegitimate**
      📌 **When to classify:**  
      - The candidate asks for direct solutions, shortcuts, or problem hints.  

      ✅ **Example:**  
      - *"Can you tell me the answer?"* → **illegitimate**  

      ---

      ### **15. inability**
      📌 **When to classify:**  
      - The candidate **explicitly states** they **cannot solve** the problem.  

      ✅ **Example:**  
      - *"I don’t know how to solve this."* → **inability**  

      ---

      ### **16. uncertainty**
      📌 **When to classify:**  
      - The candidate expresses doubt about what to do next.  

      ✅ **Example:**  
      - *"I’m not sure if this is correct."* → **uncertainty**  

      ---

      ## **Response Format**
      
      Return the classification in **exactly this format**:  
      ["class", "rationale", "distilled_candidate_dialogue"]

    """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt


def classify_candidate_dialogue_prompt_template_dev():
  prompt="""
  
  You are an agent and your task is to classify the candidate's response into different classes as defined below and explain the rationale for classifying them as such. Ensure that you classify the response with only the labels listed below and that no new label is created.

  Given:
  bot_dialogue: {bot_dialogue}
  candidate_dialogue: {candidate_dialogue}
  chat_history: {chat_history}
  distilled_candidate_dialogue: {distilled_candidate_dialogue}
  
  Before beginning to classify the candidate_dialogue (for now, avoid the distilled_candidate_dialogue and the chat_history, else you will incur penalty) please preprocess the contents of candidate_dialogue as per the following instructions:
    * If candidate_dialogue contains confirmatory responses like "yes", "no" etc. 
      - assign the response to distilled_candidate_dialogue without any preprocessing
    * If candidate_dialogue contains other kinds of texts summarize them and
      - assign the summarised text to distilled_candidate_dialogue
    * If candidate_dialogue contains grammatical errors, make the corrections (including typos, punctuations) to the text and
      - assign it finally to distilled_candidate_dialogue
  
  The following is the list of classes alongwith their definitions
  
  When classifying, the distilled_candidate_dialogue must be used (else you will incur penalty) and the 'class' must be one of:
  - technical - Candidate has attempted to solve this question 
  - illegible - Candidate utters gibberish output or non-standard words
  - irrelevant - Candidate responses that are irrelevant to the conversation
  - interview_inquiry - Candidate inquires about the interview
  - confirmation - Candidate expresses his willingness in the form of confirmatory response
  - negation - Candidate expresses his unwillingness in the form of negative response
  - clarification(specific) -  A candidate asks if specific knowledge is required
  - clarification(open) - Candidate asks a generic/non-specific expecting detailed guidance or a stepwise explanation
  - request(new_question) - Candidate explicitly requests for a new question
  - request(termination) - Candidate explicitly requests to end the interview 
  - request(proceed) - Candidate requests for a go-ahead to solve the problem
  - request(break) - Candidate requests to take a break
  - disregard - Candidate expresses disregard continuing the interview
  - illegitimate - Candidate is making illegitimate requests or statement 
  - inability - Candidate shows inability
  - uncertainty - Candidate utters a response which expresses uncertainty

  - Classify the distilled_candidate_dialogue as 'technical' when the following criteria are met:
   * The candidate has made an attempt to answer the problem

  - Classify the distilled_candidate_dialogue as 'illegible' when the following criteria are met:
    1.  **Dominant Non-Meaningful Content:**
        * The response consists primarily of random character sequences, nonsensical phrases, or words that are not found in standard dictionaries and do not appear to be technical terms or proper nouns.
        * The ratio of non-dictionary/random words to potentially meaningful words is extremely high (e.g., more than 70 percent of the words are non-dictionary/random).

    2.  **Severe Structural Incoherence:**
        * The sentence structures are so fundamentally flawed that it's impossible to discern the intended meaning, even with reasonable effort.
        * The response lacks any discernible subject-verb relationship or logical flow.
        * The dialogue lacks any coherent context with respect to the preceeding question.

    3.  **Compromised Comprehension:**
        * Even after accounting for potential typos and minor grammatical errors, the response remains incomprehensible.
        * The core intent of the candidate's answer is completely obscured.

  - Classify the distilled_candidate_dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  -Classify the distilled_candidate_dialogue as 'interview_inquiry' when the following criteria are met:
    * The candidate asks questions related to the interview process, such as its duration, structure, rescheduling or status.
    * Examples include questions like "Are we done with the interview?", "What is the duration of the interview?", "How many questions are there in this interview?", etc.
    * These inquiries are not about the specific questions being asked but focus on the overall interview process.

  -Classify the distilled_candidate_dialogue as 'confirmation' when the following criteria are met:
    * Candidate expresses his willingness in the form of confirmatory responses 
    * Examples include 'Yes', 'Yeah', 'Sure', 'Okay', 'Alright', or similar confirmatory verbose paraphrases

  -Classify the distilled_candidate_dialogue as 'negation' when the following criteria are met:
    * Candidate expresses his reluctance in the form of negative responses 
    * Examples include 'No', 'Nope', 'Not at all', 'Never', or similar verbose paraphrases    

  - Classify the distilled_candidate_dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specific terms listed in the question
    
  - Classify the distilled_candidate_dialogue as 'clarification(open)' when the following criteria are met:
    * The distilled_candidate_dialogue represents a generic/non-specific request expecting detailed guidance or a stepwise explanation  
        
  - Classify the distilled_candidate_dialogue as 'request(new_question)' when the following criteria are met:
    * The candidate explicitly states that they want alternate question.

  - Classify the distilled_candidate_dialogue as 'request(termination)' when the following criteria are met:
    * Refer to the chat_history and ensure that this is a initial request for termination and not a confirmation request
  
  - Classify the distilled_candidate_dialogue as 'request(proceed)' when the following criteria are met:
    * The candidate expresses a direct intention to proceed without any sign of doubt or uncertainty.
  
  - Classify the distilled_candidate_dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the distilled_candidate_dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language  
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the distilled_candidate_dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - Classify the distilled_candidate_dialogue as 'inability' when the following criteria are met:
    * Candidate shows inability to solve the problem  

  - Classify the distilled_candidate_dialogue as 'uncertainty' when the following criteria are met:
    * The candidate expresses uncertainty about the next steps or what action to take
    * The candidate explicitly states they do not know how to proceed or solve a problem

  You must respond ONLY in this exact format:
  ["class", "rationale", "distilled_candidate_dialogue"] 

  Requirements:
  1. List must contain exactly 3 elements
  2. No element must be empty otherwise you will be penalized
  3. Elements are defined as:
    - class: Classification or category
    - rationale: Your reasoning for generating the response
    - distilled_candidate_dialogue: the refined and corrected text
  
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt

def classify_candidate_dialogue_prompt_template_prod():
  prompt="""
  
  You are emulating a distilled_candidate_dialogue act classifier. Your task is to label the candidate's distilled_candidate_dialogue into different classes as defined below and explain the rationale for classifying them as such.

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

  - Classify the distilled_candidate_dialogue as 'technical' when the following criteria are met:
   * The candidate has made an attempt to answer the problem

  - Classify the distilled_candidate_dialogue as 'illegible' when the following criteria are met:
    * Contains non-dictionary words or random character sequences
    * Has grammatically incorrect sentence structures that make meaning unclear
    * Contains excessive typos or transcription errors

  - Classify the distilled_candidate_dialogue as 'irrelevant' when the following criteria are met:
    * Response is unrelated to the active question (follow-up or main)
    * Discusses topics outside the scope of the current question
    * Provides personal anecdotes unrelated to problem-solving
    * References main question when follow-up question should be addressed (if follow-up exists)

  -Classify the distilled_candidate_dialogue as 'interview_inquiry' when the following criteria are met:
    * The candidate asks questions related to the interview process, such as its duration, structure, or status.
    * Examples include questions like "Are we done with the interview?", "What is the duration of the interview?", "How many questions are there in this interview?", etc.
    * These inquiries are not about the specific questions being asked but focus on the overall interview process.

  -Classify the distilled_candidate_dialogue as 'confirmation' when the following criteria are met:
    * Candidate expresses his willingness in the form of confirmatory responses 
    * Examples include 'Yes', 'Yeah', 'Sure', 'Okay', 'Alright', or similar confirmatory verbose paraphrases

  -Classify the distilled_candidate_dialogue as 'negation' when the following criteria are met:
    * Candidate expresses his unwillingness in the form of negative responses 
    * Examples include 'No', 'Nope', 'Not at all', 'Never', or similar verbose paraphrases    

  - Classify the distilled_candidate_dialogue as 'clarification(specific)' when the following criteria are met:
    * The candidate asks if certain knowledge (e.g., data structures, recursion, system design) is necessary
    * The candidate asks for definitions about specific terms listed in the question
    * The question is framed to verify the interview's scope and expectations
    
  - Classify the distilled_candidate_dialogue as 'clarification(open)' when the following criteria are met:
    * The distilled_candidate_dialogue represents a generic/non-specific request expecting detailed guidance or a stepwise explanation  
        
  - Classify the distilled_candidate_dialogue as 'request(alternate_question)' when the following criteria are met:
    * The candidate explicitly states that they want alternate question.

  - Classify the distilled_candidate_dialogue as 'request(termination)' when the following criteria are met:
    * The candidate explicitly states they want to exit the interview.
    * The candidate cites an emergency requiring an immediate exit.
  
  - Classify the distilled_candidate_dialogue as 'request(proceed)' when the following criteria are met:
    * The candidate expresses a direct intention to proceed without any sign of doubt or uncertainty.
  
  - Classify the distilled_candidate_dialogue as 'request(break)' when the following criteria are met:
    * Explicit requests for a break
    * Mentions of needing a short pause
    * Time-specific break requests
  
  - Classify the distilled_candidate_dialogue as 'disregard' when the following criteria are met:
    * The candidate uses inappropriate or offensive language  
    * The candidate exhibits an unprofessional or disrespectful tone in their responses 

  - Classify the distilled_candidate_dialogue as 'illegitimate' when the following criteria are met:
    * Requests for direct solutions or complete answers
    * Questions about optimal approaches without attempting
    * Attempts to get problem-solving shortcuts
    * Making assumptions about the problem without clarification
    * Questions seeking direct solution hints without showing effort

  - Classify the distilled_candidate_dialogue as 'inability' when the following criteria are met:
    *   

  - Classify the distilled_candidate_dialogue as 'uncertainty' when the following criteria are met:
    * The candidate expresses uncertainty about the next steps or what action to take
    * The candidate explicitly states they do not know how to proceed or solve a problem

  You must respond ONLY in this exact format:
  ["class", "rationale","distilled_candidate_dialogue"] where 'rationale' is your reasoning for classifying it as such

  The list format must be preserved exactly as shown above.
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt

