# Application-wide constants

# INTERVIEW THRESHOLDS
THRESHOLD_MAX_TURNS = 10
THRESHOLD_SCORE = 5.0
THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT = 4
THRESHOLD_MAX_GUARDRAIL_COUNT = 10
THRESHOLD_MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT = 4
THRESHOLD_COMPLEXITY = 1
THRESHOLD_TOTAL_NUMBER_OF_QUESTIONS = 2

# BOT CANNED DIALOGUES
GREETING_SUFFIX = "I am Noha! I am your interviewer today. We have planned a data structures and algorithms interview with you, are you good to go?"
QUESTION_SOLVED = "Since you have solved this question, can you now start writing code for it?"
GUARDRAIL_TRIGGERED_QUESTIONS_LEFT = "It seems there is a lack of clarity. Let us move on to the next question : "
GUARDRAIL_TRIGGERED_NO_QUESTIONS_LEFT = "It seems there is a lack of clarity. Let us conclude here."
TERMINATION = "Thank you for your participation"
MAX_TURNS_TRIGGERED_QUESTIONS_LEFT = "So far so good, let us move on to the next question : "
MAX_TURNS_TRIGGERED_NO_QUESTIONS_LEFT = "We appreciate your effort on the problem! Now, can you code it for us? Let us know when you're ready."
ALL_QUESTIONS_ANSWERED = "Thank you for your participation"

# LIST OF LABELS
TECHNICAL_LABELS= ['technical', 'clarification(specific)'] #todo: refine and suitably rename the label 'technical' later
NON_TECHNICAL_LABELS= [
    "illegible", "irrelevant", "interview_inquiry", "clarification(open)", "confirmation", "negation", "request(new_question)", "request(termination)", "request(proceed)", "request(break)", "disregard", 
    "illegitimate", "inability", "uncertainty"
] #fill it later on
TECHNICAL_LABELS_TO_BE_EVALUATED = ['doubt(problem)', 'solution']
TECHNICAL_LABELS_NOT_TO_BE_EVALUATED= ['doubt(concept)']

# SESSION INITIALIZATION DEFAULTS
DEF_INTERVIEW_ID = None  # Set dynamically
DEF_TURN_NUMBER = 0
DEF_CONSECUTIVE_TERMINATION_REQUEST_COUNT = 0
DEF_BOT_DIALOGUE = None  # Set dynamically
DEF_GUARDRAIL_COUNT = 0
DEF_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT = 0
DEF_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT = 0
DEF_TERMINATION = False
DEF_CURRENT_QUESTION = ""
DEF_NEXT_ACTION = "Pass"
DEF_QUESTIONS_ASKED = []
DEF_BOT_DIALOGUE_TYPE = "greeting"
DEF_COMPLEXITY = 1

# CHAT HISTORY DEFAULTS
DEF_INTERVIEW_ID = None # Set dynamically
DEF_QUESTION_ID = None # Set later dynamically in get_next_question function
DEF_BOT_DIALOGUE_TYPE = 'greeting'
DEF_BOT_DIALOGUE = None # Set dynamically
DEF_CANDIDATE_DIALOGUE = None # Set dynamically from client as response to first greeting message
DEF_DISTILLED_CANDIDATE_DIALOGUE = None # Set dynamically from candidate_classifier