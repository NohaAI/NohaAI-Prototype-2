# Application-wide constants

# INTERVIEW THRESHOLDS ############################################################
THRESHOLD_MAX_TURNS = 15
THRESHOLD_SCORE = 10.0
THRESHOLD_MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT = 4
THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT = 4
THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_NO_PRIMARY_QUESTION_GUARDRAIL_COUNT = 2
THRESHOLD_MAX_GUARDRAIL_COUNT = 10
THRESHOLD_COMPLEXITY = 1
THRESHOLD_TOTAL_NUMBER_OF_QUESTIONS = 2

# BOT CANNED DIALOGUES ############################################################
GREETING_SUFFIX_DEV = "Ready?"
GREETING_SUFFIX = "I am Noha! I am your interviewer today. We have planned a data structures and algorithms interview with you, are you good to go?"
QUESTION_SOLVED = "Okay, now that you have answered the algorithmic aspects, can you begin writing the code ?"
GUARDRAIL_TRIGGERED_QUESTIONS_REMAIN = "Sorry, there seems to be a lack of clarity in your responses. Let us move on to the next question: "
GUARDRAIL_TRIGGERED_NO_QUESTIONS_REMAIN = "Sorry, there seems to be a lack of clarity in your responses. Let us conclude here."
GUARDRAIL_TRIGGERED_NO_PRIMARY_QUESTION = "I suppose we should go back to beginning the interview, are you ready for the questions?"
TERMINATION = "Thank you for your participation"
MAX_TURNS_TRIGGERED_QUESTIONS_REMAIN = "So far so good, let us move on to the next question : "
MAX_TURNS_TRIGGERED_NO_QUESTIONS_REMAIN = "We appreciate your responses so far! Now, can you code it for us? Let us know when you're ready."
ALL_QUESTIONS_ANSWERED = "Thank you for your participation"

# LIST OF LABELS ################################################################
TECHNICAL_LABELS = ['technical', 'clarification(specific)'] #todo: refine and suitably rename the label 'technical' later
NON_TECHNICAL_LABELS = [
    "illegible", "irrelevant", "interview_inquiry", "clarification(open)", "confirmation", "negation", "request(new_question)", "request(termination)", "request(proceed)", "request(break)", "disregard", 
    "illegitimate", "inability", "uncertainty"
] #fill it later on
NON_TECHNICAL_UNREASONABLE_LABELS = [
    "illegible", "irrelevant", "clarification(open)", "request(new_question)", "request(proceed)", "request(break)", "disregard", 
    "illegitimate", "inability", "uncertainty"
] 
TECHNICAL_LABELS_TO_BE_EVALUATED = ['doubt(problem)', 'solution']
TECHNICAL_LABELS_NOT_TO_BE_EVALUATED= ['doubt(concept)']

# SESSION INITIALIZATION DEFAULTS ################################################
DEF_INTERVIEW_ID = None  # Set dynamically
DEF_BOT_DIALOGUE = None  # Set dynamically
DEF_CANDIDATE_DIALOGUE = None # Set dynamically
DEF_TURN_NUMBER = 0
DEF_CONSECUTIVE_TERMINATION_REQUEST_COUNT = 0
DEF_GUARDRAIL_COUNT = 0
DEF_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT = 0
DEF_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT = 0
DEF_TERMINATION = False
DEF_PRIMARY_QUESTION = None
DEF_NEXT_ACTION = "Pass"
DEF_QUESTIONS_ASKED = []
DEF_BOT_DIALOGUE_TYPE = None
DEF_COMPLEXITY = 1
DEF_LABEL_CLASS1 = None
DEF_LABEL_CLASS2 = None
DEF_SOLUTION_CLASSIFIER_EXECUTED = False

# CHAT HISTORY DEFAULTS ###########################################################
### DEF_INTERVIEW_ID = None # have been already defined in session defaults section
DEF_QUESTION_ID = None # Set dynamically in initialize
### DEF_BOT_DIALOGUE = None # have been already defined in session defaults section
### DEF_BOT_DIALOGUE_TYPE = 'greeting' # have been already defined in session defaults section
### DEF_CANDIDATE_DIALOGUE = None # Set dynamically from client as response to first greeting message
DEF_DISTILLED_CANDIDATE_DIALOGUE = None # Set dynamically from candidate_classifier

# ASSESSMENT DEFAULTS ###########################################################
### DEF_INTERVIEW_ID = None # have been already defined in session defaults section
### DEF_QUESTION_ID = None # have been already defined in chat history defaults section
DEF_PRIMARY_QUESTION_SCORE = 0.0
DEF_ASSESSMENT_PAYLOADS = None

# BOT NAME
BOT_NAME = "Noha AI"
# ASSESSMENT DATA DEFAULTS ###########################################################
ASSESSMENT_PAYLOAD_SCHEMA_PATH = "src.schemas.evaluation"
# ASSESSMENT_PAYLOAD_SCHEMA = "assessment_payload.json"
ASSESSMENT_PAYLOAD_SCHEMA = "assessment_payload_longest_8criterion.json"

#LIVE CODE WHILE DEVELOPING
DEVELOPER_LIVE_CODE = "333333"