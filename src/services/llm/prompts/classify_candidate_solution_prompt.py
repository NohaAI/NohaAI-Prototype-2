from langchain_core.prompts import ChatPromptTemplate

def classify_candidate_solution_prompt_template():

  prompt = """
  You are emulating a candidate answer classifier. Your task is to label the candidate's answer into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  primary_question: {primary_question}
  bot_dialogue: {bot_dialogue}
  candidate_solution: {candidate_solution}
  chat_history: {chat_history}

  YOU MUST RESPOND IN THE FOLLOWING FORMAT:
  ["class","rationale"]

  'rationale' is your reasoning for classifying the candidate_solution, which is actually a candidate_solution to the primary_question in this case

 class must be one of:
  - "solution": The candidate_solution contains either: Complete implementation details/code, step-by-step approach, specific algorithmic elements with clear purpose, or technical approach that includes HOW components will be used

  - "doubt(concept)": The candidate_solution seeks to clarify a doubt or doubts about fundamental programming/algorithmic concepts referenced in the primary_question or bot_dialogue (if present)

  - "doubt(problem)": The candidate_solution seeks to clarify a specific doubt or specific doubts about the primary_question or bot_dialogue (if present)

  """
  
  # Note: Choose the most appropriate single classification based on the primary characteristic of the candidate_solution. If multiple categories could apply, select the most significant one that best captures the key attribute of candidate_solution
  classify_candidate_answer_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_answer_prompt


def classify_candidate_answer_prompt_template_current():
  prompt="""
  You are emulating a candidate answer classifier. Your task is to label the candidate's answer into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  Question: {question}
  Followup Question: {follow_up_question}
  Answer: {answer}
  Chat History: {chat_history}

  YOU MUST RESPOND IN THE FOLLOWING FORMAT:
  ["class","rationale"]

  class must be one of :
  - correct(partial)
    * The answer contains valid elements but includes errors, omissions, or misunderstandings in key areas.
    Example: A candidate correctly identifies a sorting algorithm but misapplies its time complexity.

  - incorrect
    * The answer is fundamentally flawed or demonstrates a misunderstanding of core concepts.
    Example: Claiming "binary search works on unsorted arrays."

  - completeness(superficial)
    * The answer addresses the surface-level problem but lacks critical details or deeper analysis.
    Example: "Use a hashmap to solve it" without explaining collision handling or implementation steps.

  - completeness(comprehensive)
    * The answer covers edge cases, optimizations, and trade-offs thoroughly.
    Example: Discussing time/space complexity, handling empty inputs, and comparing alternative approaches.

  - algorithm(optimal)
    * The solution uses the most efficient algorithm/data structure for the problem constraints.
    Example: Proposing O(n) time and O(1) space for a problem where brute force would be O(n²).

  - algorithm(suboptimal)
    * The solution works but uses unnecessary complexity, redundancy, or inefficiency.
    Example: Solving a problem with nested loops when a sliding window would suffice.

  - algorithm(innovative)
    * The answer proposes a creative or non-obvious solution beyond standard methods.
    Example: Combining two paradigms (e.g., dynamic programming with greedy heuristics) for a novel approach.

  - algorithm(conventional)
    * The answer follows textbook methods but lacks adaptation to the specific problem.
    Example: Defaulting to recursion for a problem better solved iteratively.

  - communication(clear)
    * The explanation is logically structured, jargon-free, and easy to follow.
    Example: Breaking down steps with analogies (e.g., "Imagine the array as a sliding window...").

  - communication(unclear)
    * The explanation is disjointed, overly technical, or lacks flow.
    Example: Jumping between ideas without connecting them (e.g., "Use BFS... then maybe backtracking?").

  - communication(verbose)
    * The answer includes unnecessary details or over-explains trivial points.
    Example: Spending 5 minutes explaining loops to someone familiar with programming.

  - communication(concise)
    * The answer is direct and avoids redundancy while retaining critical details.

  - approach(adaptable)
    * The candidate revises their approach when prompted or acknowledges gaps.
    Example: "I initially thought of brute force, but let me optimize it with memoization."

  - approach(rigid)
    * The candidate sticks to an initial (flawed) approach despite hints or edge cases.

  - approach(hypothetical)
    * The answer focuses on theoretical possibilities without concrete implementation steps.
    Example: "Maybe a graph traversal could work here" without specifying how.

  - verification(done)
    * The candidate explicitly tests their solution against edge cases or invalid inputs.
    Example: "Let me check for empty arrays and negative numbers in the input."

  - verification(clarification)
    * The candidate is trying to clarify some information regarding the question
    Example: "Let me clarify the scope I would assume that the string would contain only alphabets and do no contain numbers or special characters palindrome is when a string is equal to the reverse of a string please confirm if my understanding is correct."
    
  - verification(not_done)
    * The answer assumes correctness without verification and clarification.

  'rationale' is your reasoning for classifying candidate answer as such
  """
  classify_candidate_answer_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_answer_prompt
