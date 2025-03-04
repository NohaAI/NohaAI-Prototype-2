from datetime import datetime
import json
from src.services.workflows.answer_evaluator import evaluate_answer
from src.dao.question import get_random_question_metadata
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.services.workflows.bot_dialogue_generatorv2 import generate_dialogue
from src.services.workflows.answer_classifer import classify_candidate_technical_dialogue
from src.utils.logger import get_logger
from src.utils.response_helper import get_assessment_payload
from src.schemas.taxonomy import TECHNICAL_LABELS, TECHNICAL_LABELS_NOT_TO_BE_EVALUATED, TECHNICAL_LABELS_TO_BE_EVALUATED, NON_TECHNICAL_LABELS
from src.services.workflows.interview_thresholds import COMPLEXITY, TOTAL_NUMBER_OF_QUESTIONS
from src.services.workflows.interview_thresholds import MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT, MAX_GUARDRAIL_COUNT,MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT,MAX_TURNS,SCORE_THRESHOLD
from src.schemas.messages import QUESTION_SOLVED, GUARDRAIL_TRIGGERED_QUESTIONS_LEFT, GUARDRAIL_TRIGGERED_NO_QUESTIONS_LEFT, MAX_TURNS_TRIGGERED_NO_QUESTIONS_LEFT, MAX_TURNS_TRIGGERED_QUESTIONS_LEFT, ALL_QUESTIONS_ANSWERED, TERMINATION
from src.dao.data_objects.assessment_payload import AssessmentPayloadRecord
logger = get_logger(__name__)

async def process_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record):
    session_state['contiguous_non_technical_guardrail_count'] = 0
    candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale = await classify_candidate_technical_dialogue(session_state['bot_dialogue'], distilled_candidate_dialogue, filtered_chat_history, session_state['current_question']) # refactor into candidate tech dialogue
# bot_dialogue, candidate_dialogue, distilled_chat_history, question
    
    if candidate_technical_dialogue_label in TECHNICAL_LABELS_TO_BE_EVALUATED:
        logger.info(f"ENTERED EVALUATE ANSWER FOR TURN {session_state['turn_number']}")
        assessment_payload_recieved_from_evaluate_answer, assessment_payload_rationale = await evaluate_answer(session_state['bot_dialogue'], distilled_candidate_dialogue, filtered_chat_history, assessment_payload_record.return_assessment_payload(session_state['interview_id'], session_state['questions_asked'][-1]))
        assessment_payload_record.update_record(session_state['interview_id'], session_state['questions_asked'][-1], assessment_payload_recieved_from_evaluate_answer['final_score'], assessment_payload_recieved_from_evaluate_answer)
        # question_id, question, candidate_answer, eval_distribution, filtered_chat_history, prev_eval = None
        logger.info(f"EXITED EVALUATE ANSWER FOR TURN : {session_state['turn_number']}")
    else:
        session_state[''] +=1 
    session_state['turn_number'] +=1

    logger.info(f"ENTERED GENERATE DIALOGUE : {session_state['turn_number']}")

    logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']} \n CLASS LABEL : {candidate_technical_dialogue_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['bot_dialogue']} \n CANDIDATE DIALOGUE : {distilled_candidate_dialogue} \n CHAT HISTORY : {filtered_chat_history} \n CANDIDATE ANSWER CLASSIFICATION RATIONALE : {candidate_technical_dialogue_classification_rationale} \n ASSESSMENT PAYLOAD : {assessment_payload_record} ")

    bot_dialogue, bot_dialogue_rationale, bot_dialogue_subcriterion, session_state['next_action'] = await generate_dialogue(candidate_technical_dialogue_label, filtered_chat_history, distilled_candidate_dialogue,session_state['current_question'], assessment_payload_record.return_assessment_payload(session_state['interview_id'], session_state['questions_asked'][-1]), session_state['bot_dialogue'], candidate_technical_dialogue_classification_rationale)
    session_state['bot_dialogue_type'] = 'follow-up'
    logger.info(f"EXITED GENERATE DIALOGUE FOR {session_state['turn_number']}")
    session_state['bot_dialogue'] = bot_dialogue
    return candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale,  bot_dialogue_rationale, bot_dialogue_subcriterion, assessment_payload_rationale, session_state, assessment_payload_record

async def process_non_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record, candidate_dialogue_label):
    if candidate_dialogue_label == 'request(termination)':
        session_state['consecutive_termination_request_count'] +=1
    else:
        session_state['consecutive_termination_request_count'] = 0

    logger.info(f"ENTERED BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']}")
    logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']} \n CLASS LABEL : {candidate_dialogue_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['bot_dialogue']} \n CANDIDATE DIALOGUE : {distilled_candidate_dialogue} \n CHAT HISTORY : {filtered_chat_history} \n  ASSESSMENT PAYLOAD : {assessment_payload_record} ")

    bot_dialogue, bot_dialogue_rationale, but_dialogue_subcriterion, session_state['next_action'] = await generate_dialogue(candidate_dialogue_label, filtered_chat_history, distilled_candidate_dialogue, session_state['current_question'], assessment_payload_record.return_assessment_payload(session_state['interview_id'], session_state['questions_asked'][-1]), session_state['bot_dialogue'],rationale = None)
    session_state['bot_dialogue_type'] = 'follow-up'
    
    logger.info(f"EXITED BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']}")
    session_state['bot_dialogue']=bot_dialogue
    session_state['turn_number'] += 1
    return bot_dialogue_rationale, but_dialogue_subcriterion, session_state

async def generate_action_overrides(session_state, assessment_payload_record):
    if(assessment_payload_record.return_final_score(session_state['interview_id'], session_state['questions_asked'][-1]) >= SCORE_THRESHOLD):
        session_state['termination'] = True      
        session_state['bot_dialogue'] = QUESTION_SOLVED
    # Max Conversation turns check
    if session_state['turn_number'] >= (MAX_TURNS * len(session_state['questions_asked'])):
        if len(session_state['questions_asked']) >= TOTAL_NUMBER_OF_QUESTIONS:  #discuss whether to keep a list or an int that tells number of questions to be asked
            session_state['bot_dialogue'] = MAX_TURNS_TRIGGERED_QUESTIONS_LEFT
            session_state['next_action'] = 'get_new_question'
        else:
            session_state['termination'] = True      
            session_state['bot_dialogue'] = MAX_TURNS_TRIGGERED_NO_QUESTIONS_LEFT
            
    # Contiguous guardrail and unacceptable answer check breach check
    logger.info(f"SESSION STATE BEFORE CALLING MAX COUNTS : \n {session_state}")         
    if session_state['contiguous_non_technical_guardrail_count'] >= MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT or session_state['contiguous_technical_guardrail_count'] >= MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT: 
        if len(session_state['questions_asked']) >= TOTAL_NUMBER_OF_QUESTIONS :
            session_state['next_action'] = 'get_new_question'
            session_state['bot_dialogue'] = GUARDRAIL_TRIGGERED_QUESTIONS_LEFT
        else:                                   
            session_state['termination'] = True
            session_state['bot_dialogue'] = GUARDRAIL_TRIGGERED_NO_QUESTIONS_LEFT

    if session_state['consecutive_termination_request_count'] == 2:
        session_state['next_action'] == "terminate_interview_confirmation"

    return session_state, assessment_payload_record

async def perform_actions(session_state, assessment_payload_record):

    if(session_state['next_action'] == 'get_new_question'):
        if(len(session_state['questions_asked']) == 0):
            session_state['complexity'] = COMPLEXITY #initial complexity set to 1 to be handeled later on accordingly
            question_metadata=await get_random_question_metadata(session_state['complexity'], session_state['questions_asked']) # should take a list as parameter and check whether these lists of questions are already asked in the database
            question=question_metadata['question']
            question_id = question_metadata['question_id']
            session_state['questions_asked'].append(question_id)

            session_state['current_question'] = question
            session_state['bot_dialogue'] = session_state['current_question']

            session_state = {
            "interview_id": session_state['interview_id'],
            "turn_number": session_state['turn_number'],
            "consecutive_termination_request_count": 0,
            "bot_dialogue": session_state['bot_dialogue'],
            "guardrail_count": 0,
            "contiguous_technical_guardrail_count": 0,
            "contiguous_non_technical_guardrail_count": 0,
            "termination": False,
            "current_question": session_state['current_question'],
            "next_action": "Pass",
            "questions_asked": session_state['questions_asked'],
            "bot_dialogue_type": "question",
            "complexity": session_state['complexity']
            }
            assessment_payload = get_assessment_payload() #used for initializing assessement_payload for a new question
            assessment_payload_record.add_record(session_state['interview_id'], session_state['questions_asked'][-1], assessment_payload['final_score'], assessment_payload)
        elif len(session_state['questions_asked']) >= TOTAL_NUMBER_OF_QUESTIONS :
            session_state['termination'] = True
            session_state['bot_dialogue'] = ALL_QUESTIONS_ANSWERED
        else:
            session_state['complexity'] -= 1 #atm questions will become easier since we are not giving another question when candidate is done answering the question
            question_metadata=await get_random_question_metadata(session_state['complexity'], session_state['questions_asked']) # should take a list as parameter and check whether these lists of questions are already asked in the database
            question=question_metadata['question']
            question_id = question_metadata['question_id']
            session_state['questions_asked'].append(question_id)

            session_state['current_question'] = question
            session_state['bot_dialogue'] = session_state['bot_dialogue'] + session_state['current_question']

            session_state = {
            "interview_id": session_state['interview_id'],
            "turn_number": session_state['turn_number'],
            "consecutive_termination_request_count": 0,
            "bot_dialogue": session_state['bot_dialogue'],
            "guardrail_count": 0,
            "contiguous_technical_guardrail_count": 0,
            "contiguous_non_technical_guardrail_count": 0,
            "termination": False,
            "current_question": session_state['current_question'],
            "next_action": "Pass",
            "questions_asked": session_state['questions_asked'],
            "bot_dialogue_type": "new_question",
            "complexity": session_state['complexity']
            }
            assessment_payload = get_assessment_payload() #used for initializing assessement_payload for a new question
            assessment_payload_record.add_record(session_state['interview_id'], session_state['questions_asked'][-1], assessment_payload['final_score'], assessment_payload)

    if(session_state['next_action'] == "terminate_interview_confirmation"):
        session_state['termination']=True
        session_state['bot_dialogue'] = TERMINATION 
    
    return session_state, assessment_payload_record
#TODO: CHANGE LOGGING FOR EVAL ANSWER ACC TO NEW ASSESSMENT PAYLOAD
def log_data(candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_rationale, candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale, assessment_payload_record, assessment_payload_rationale, bot_dialogue_subcriterion ,candidate_dialogue_label, session_state, candidate_dialogue_rationale):
    
    log_file = "rationale_logs.txt"
    class_label = candidate_dialogue_label
    log_entry = f"#### ************ CONVERSATION TURN {session_state['turn_number']} ************\n"

    if class_label:
        log_entry += f"**ORIGINAL CANDIDATE DIALOGUE:** {candidate_dialogue}\n"
        log_entry += f"**DISTILLED CANDIDATE DIALOGUE:** {distilled_candidate_dialogue}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL:** {class_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL RATIONALE:** {candidate_dialogue_rationale}\n\n"

    log_entry += f"**ACTION FLAG:** {session_state['next_action']}\n\n"

    if class_label not in ['technical', 'clarification(specific)']:
        log_entry += f"**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
        log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
    else:
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II:** {candidate_technical_dialogue_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II RATIONALE:** {candidate_technical_dialogue_classification_rationale}\n\n"
        
        if candidate_technical_dialogue_label  in TECHNICAL_LABELS_TO_BE_EVALUATED:
            log_entry += "**ANSWER EVALUATION**\n"
            subcriteria_score_list = []
            
            for idx, dct in enumerate(assessment_payload_record.return_assessment_payload['assessment']):
                if idx % 3 == 0:
                    log_entry += "\n"
                log_entry += f"\t{dct}\n"
                k = list(dct)[0]
                subcriteria_score_list.append(dct[k])
            
            log_entry += f"\n**ANSWER EVALUATION RATIONALE : ** \n"
            for idx, item in enumerate(assessment_payload_rationale):
                log_entry += f"\t\t\t {idx+1} : {item} \n"
            
            log_entry += f"\n**SUBCRITERIA SCORES:** {subcriteria_score_list}\n"
            log_entry += f"\n**EVALUATION DISTRIBUTION:** {assessment_payload_record.return_assessment_payload['criteria_scores']}\n"
            log_entry += f"\n**FINAL SCORE:** {session_state['final_score']}\n"
            log_entry += f"\n**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
            log_entry += f"\n**SUBCRITERION:** {bot_dialogue_subcriterion}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
        else:
            log_entry += f"**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"

    # Append log entry with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry_with_timestamp = f"{timestamp}\n{log_entry}\n"

    # Write to file
    with open(log_file, "a") as file:
        file.write(log_entry_with_timestamp)

async def get_next_response(candidate_dialogue, session_state, chat_history, assessment_payload_record):
    
    logger.info("############################################################################################################")
    logger.info(f"USER INPUT AFTER ENTERING get_next_response FOR TURN {session_state['turn_number']} :\n {candidate_dialogue}")
    logger.info(f"SESSION STATE RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {session_state}")
    logger.info(f"USER CHAT HISTORY RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {chat_history}")
    logger.info(f"ASSESSMENT PAYLOAD RECORD RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {assessment_payload_record}")

    candidate_dialogue_label, candidate_dialogue_rationale, distilled_candidate_dialogue = await classify_candidate_dialogue(session_state['bot_dialogue'], candidate_dialogue, chat_history.filtered_chat_history(session_state['interview_id'], None))

    if len(session_state['questions_asked']) == 0:
       
        if candidate_dialogue_label == 'confirmation':
            session_state, assessment_payload_record = await perform_actions(session_state, assessment_payload_record)
            chat_history.add_record(session_state['interview_id'], session_state['questions_asked'][-1], session_state['bot_dialogue_type'], session_state['bot_dialogue'], candidate_dialogue, distilled_candidate_dialogue) #DISTITLLATION FOR CANDIDATES WILLINGNESS IS NOT NECESSARY         
        else:
            chat_history.add_record(session_state['interview_id'], None, session_state['bot_dialogue_type'], session_state['bot_dialogue'], candidate_dialogue, distilled_candidate_dialogue) #at the moment you dont have question_id so it will be none
        session_state['turn_number'] += 1 
    else:
        chat_history.add_record(session_state['interview_id'], session_state['questions_asked'][-1], session_state['bot_dialogue_type'], session_state['bot_dialogue'], candidate_dialogue, distilled_candidate_dialogue)
        filtered_chat_history = chat_history.filtered_chat_history(session_state['interview_id'], session_state['questions_asked'][-1])

        if candidate_dialogue_label in TECHNICAL_LABELS:
            candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale,  bot_dialogue_rationale, bot_dialogue_subcriterion, assessment_payload_rationale, session_state, assessment_payload_record = await process_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record)
        else:
            bot_dialogue_rationale, but_dialogue_subcriterion, session_state = await process_non_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record, candidate_dialogue_label)
        
        session_state, assessment_payload_record = await generate_action_overrides(session_state, assessment_payload_record)
        
        session_state, assessment_payload_record = await perform_actions(session_state, assessment_payload_record)

    #log_data(candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_rationale, candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale, assessment_payload_record, assessment_payload_rationale, bot_dialogue_subcriterion ,candidate_dialogue_label, session_state, candidate_dialogue_rationale) # toggle on/off if you want data to be logged
        
    logger.info(f"SESSION STATE BEFORE RETURNING FROM get_noha_dialogue FOR TURN {session_state['turn_number']} \n {session_state}")
    return session_state['bot_dialogue'] , session_state, chat_history, assessment_payload_record

