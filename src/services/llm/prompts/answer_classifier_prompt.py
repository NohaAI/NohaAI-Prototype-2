from langchain_core.prompts import ChatPromptTemplate

def classify_candidate_answer_prompt_template():
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

  - clarity(clear)
    * The explanation is logically structured, jargon-free, and easy to follow.
    Example: Breaking down steps with analogies (e.g., "Imagine the array as a sliding window...").

  - clarity(unclear)
    * The explanation is disjointed, overly technical, or lacks flow.
    Example: Jumping between ideas without connecting them (e.g., "Use BFS... then maybe backtracking?").

  - clarity(verbose)
    * The answer includes unnecessary details or over-explains trivial points.
    Example: Spending 5 minutes explaining loops to someone familiar with programming.

  - clarity(concise)
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
def classify_candidate_answer_prompt_template_Ritesh():
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

  - clarity(clear)
    * The explanation is logically structured, jargon-free, and easy to follow.
    Example: Breaking down steps with analogies (e.g., "Imagine the array as a sliding window...").

  - clarity(unclear)
    * The explanation is disjointed, overly technical, or lacks flow.
    Example: Jumping between ideas without connecting them (e.g., "Use BFS... then maybe backtracking?").

  - clarity(verbose)
    * The answer includes unnecessary details or over-explains trivial points.
    Example: Spending 5 minutes explaining loops to someone familiar with programming.

  - clarity(concise)
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

  - verification(not_done)
    * The answer assumes correctness without verification and clarification.

  'rationale' is your reasoning for classifying candidate answer as such
  """
  classify_candidate_answer_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_answer_prompt


def classify_candidate_answer_prompt_template_v1_deepseek():
  prompt="""
  You are emulating a candidate answer classifier. Your task is to label the candidate's answer into different classes as defined below and explain the rationale for classifying them as such.

  Given:
  question: {question}
  answer: {answer}
  chat history: {chat history}

  class must be one of :
  1. Correct(Partial)
  The answer contains valid elements but includes errors, omissions, or misunderstandings in key areas.
  Example: A candidate correctly identifies a sorting algorithm but misapplies its time complexity.

  1. Incorrect
  The answer is fundamentally flawed or demonstrates a misunderstanding of core concepts.
  Example: Claiming "binary search works on unsorted arrays."

  2. Completeness & Depth(Superficial)
  The answer addresses the surface-level problem but lacks critical details or deeper analysis.
  Example: "Use a hashmap to solve it" without explaining collision handling or implementation steps.

  2. Completeness & Depth(Comprehensive)
  The answer covers edge cases, optimizations, and trade-offs thoroughly.
  Example: Discussing time/space complexity, handling empty inputs, and comparing alternative approaches.

  3. Technical Approach(Optimal)
  The solution uses the most efficient algorithm/data structure for the problem constraints.
  Example: Proposing O(n) time and O(1) space for a problem where brute force would be O(n²).

  3. Technical Approach(Suboptimal)
  The solution works but uses unnecessary complexity, redundancy, or inefficiency.
  Example: Solving a problem with nested loops when a sliding window would suffice.

  3. Technical Approach(Innovative)
  The answer proposes a creative or non-obvious solution beyond standard methods.
  Example: Combining two paradigms (e.g., dynamic programming with greedy heuristics) for a novel approach.

  3. Technical Approach(Conventional)
  The answer follows textbook methods but lacks adaptation to the specific problem.
  Example: Defaulting to recursion for a problem better solved iteratively.

  4. Communication & Clarity(Clear)
  The explanation is logically structured, jargon-free, and easy to follow.
  Example: Breaking down steps with analogies (e.g., "Imagine the array as a sliding window...").

  4. Communication & Clarity(Unclear)
  The explanation is disjointed, overly technical, or lacks flow.
  Example: Jumping between ideas without connecting them (e.g., "Use BFS... then maybe backtracking?").

  4. Communication & Clarity(Verbose)
  The answer includes unnecessary details or over-explains trivial points.
  Example: Spending 5 minutes explaining loops to someone familiar with programming.

  4. Communication & Clarity(Concise)
  The answer is direct and avoids redundancy while retaining critical details.

  5. Problem-Solving Behavior(Adaptable)
  The candidate revises their approach when prompted or acknowledges gaps.
  Example: "I initially thought of brute force, but let me optimize it with memoization."

  5. Problem-Solving Behavior(Rigid)
  The candidate sticks to an initial (flawed) approach despite hints or edge cases.

  5. Problem-Solving Behavior(Hypothetical)
  The answer focuses on theoretical possibilities without concrete implementation steps.
  Example: "Maybe a graph traversal could work here" without specifying how.

  6. Validation & Testing(Validated)
  The candidate explicitly tests their solution against edge cases or invalid inputs.
  Example: "Let me check for empty arrays and negative numbers in the input."

  6. Validation & Testing(Untested)
  The answer assumes correctness without verification.

  7. Conceptual Understanding(Deep)
  The answer demonstrates mastery of underlying principles (e.g., algorithmic trade-offs, system design fundamentals).

  7. Conceptual Understanding(Shallow)
  The answer relies on memorization without understanding "why" a solution works.
  """
  classify_candidate_dialogue_prompt=ChatPromptTemplate.from_template(template=prompt)
  return classify_candidate_dialogue_prompt