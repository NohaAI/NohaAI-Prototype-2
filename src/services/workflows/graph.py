from datetime import datetime
import json
from src.services.workflows.solution_evaluator import evaluate_solution
from src.dao.question import get_random_question_metadata
from src.dao.assessment import AssessmentDAO
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.services.workflows.bot_dialogue_generator import generate_dialogue
from src.services.workflows.candidate_solution_classifier import classify_candidate_solution
from src.utils.logger import get_logger, write_to_report
from src.dao.assessment_data.assessment_record import AssessmentRecord
from src.utils import helper as helper
from src.config import constants as CONST

logger = get_logger(__name__)


###############################################################################################################################
################################################### VALIDATE INPUT ############################################################
###############################################################################################################################

def validate_input(session_state, chat_history, assessment_payload_record):
    if chat_history is None:
        raise ValueError("CHAT HISTORY RECEIVED EMPTY")
    if assessment_payload_record is None:
        raise ValueError("ASSESSMENT PAYLOAD RECORD RECEIVED EMPTY")
    if session_state is None:
        raise ValueError("SESSION STATE RECEIVED EMPTY")
    
    expected_session_state_types = {
        'interview_id': int,
        'turn_number': int,
        'consecutive_termination_request_count': int,
        'bot_dialogue': str,
        'candidate_dialogue': str,
        'guardrail_count': int,
        'contiguous_technical_guardrail_count': int,
        'contiguous_non_technical_guardrail_count': int,
        'termination': bool,
        'current_question': str,
        'next_action': str,
        'questions_asked': list,
        'bot_dialogue_type': str,
        'complexity': int
    }
    
    for key, expected_type in expected_session_state_types.items():
        if key not in session_state or not isinstance(session_state[key], expected_type):
            raise ValueError(f"{key} is missing, null, or not of type {expected_type}")
        

###############################################################################################################################
################################################### PROCESS TECHNICAL #########################################################
###############################################################################################################################  
    
async def process_technical(session_state, chat_history, assessment):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [process_technical] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    session_state['contiguous_non_technical_guardrail_count'] = 0

    ##### CALL CLASSIFY DIALOGUE (II CLASSIFICATION) #######
    label_class2, candidate_solution_rationale = await classify_candidate_solution(session_state, chat_history)

    #### setting the session_state 'solution classifier executed' flag to True
    session_state["solution_classifier_executed"] = True

    
    if label_class2 in CONST.TECHNICAL_LABELS_TO_BE_EVALUATED:
        ########################## CALL (BOTH ==> SOLUTION EVALUATOR + GENERATE DIALOGUE) IN PROCESS TECHNICAL #####################
        
        ##### CALL (EVALUATOR) IN PROCESS TECHNICAL ######
        assessment, solution_evaluator_rationale = await evaluate_solution(session_state, chat_history, assessment)

        ##### CALL (GENERATE DIALOGUE) IN PROCESS TECHNICAL ######
        bot_dialogue_rationale, bot_dialogue_causal_subcriterion = await generate_dialogue(session_state, chat_history, assessment, solution_evaluator_rationale)

    else:
        session_state['contiguous_technical_guardrail_count'] +=1 

        ##### CALL (GENERATE DIALOGUE) IN PROCESS TECHNICAL ######
        bot_dialogue_rationale, bot_dialogue_causal_subcriterion = await generate_dialogue(session_state, chat_history, assessment, candidate_solution_rationale)

    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [process_technical] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return bot_dialogue_rationale, bot_dialogue_causal_subcriterion


###############################################################################################################################
################################################### PROCESS NON TECHNICAL  ####################################################
###############################################################################################################################

async def process_non_technical(session_state, chat_history, assessment, candidate_dialogue_rationale):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [process_non_technical] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)
    
    # As of 09Mar25 the labels that merit a guardrail increment are as follows
    # NON_TECHNICAL_UNREASONABLE_LABELS = [
    # "illegible", "irrelevant", "clarification(open)", "request(new_question)", "request(proceed)", "request(break)", "disregard", 
    # "illegitimate", "inability", "uncertainty" ] 

    if session_state['label_class1'] in CONST.NON_TECHNICAL_UNREASONABLE_LABELS:
        session_state['contiguous_non_technical_guardrail_count'] += 1

    # the non-technical but reasonable labels are not penalised but in case, required handled specially hereafter
    # handling for class label 'request(termination)
    if session_state['label_class1'] == 'request(termination)':
        session_state['consecutive_termination_request_count'] +=1
    else:
        session_state['consecutive_termination_request_count'] = 0

    
    ##### CALL GENERATE DIALOGUE IN PROCESS NON-TECHNICAL ######
    bot_dialogue_rationale, bot_dialogue_causal_subcriterion = await generate_dialogue(session_state, chat_history, assessment, candidate_dialogue_rationale)
    
    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [process_non_technical] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return bot_dialogue_rationale, bot_dialogue_causal_subcriterion


###############################################################################################################################
############################################### GENERATE ACTION OVERRIDES #####################################################
###############################################################################################################################

async def generate_action_overrides(session_state, chat_history, assessment):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [generate_action_overrides] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    ### RESET OR REINITIALIZE the relevant values immediately after the dialogue generator which is this function call
    ### or maybe push these later in perform_actions function
    ############################
    session_state['turn_number'] += 1
    session_state['solution_classifier_executed'] = False
    

    if session_state['next_action'] == 'get_primary_question':
        session_state['bot_dialogue_type'] = 'primary_question'
        chat_history[-1]['bot_dialogue_type'] = 'primary_question'
    else:
        session_state['bot_dialogue_type'] = 'follow-up'
        chat_history[-1]['bot_dialogue_type'] = 'follow-up'
    ############################


    # Check if the consecutive termination count is equal to 2;  exit interview
    if session_state['consecutive_termination_request_count'] == 2:
        session_state['next_action'] = "terminate_interview_confirmation"
    
    # Check if the final score exceeds the decided threshold score; move to a new topic question
    elif (assessment[-1]["primary_question_score"] >= CONST.THRESHOLD_SCORE):
        session_state['termination'] = True     #TODO: DANGEROUS looks like a wrong assignment
        session_state['bot_dialogue'] = CONST.QUESTION_SOLVED
        chat_history[-1]['bot_dialogue'] = CONST.QUESTION_SOLVED
    
    # Check if max turns have exceeded the threshold decided, and all this while checking 
    #   - length of questions asked list is greater than 0 else the threshold will evaluate to zero
    #   - calculate threshold score while multiplying with the number of questions
    #   - if total number of primary questions is within the limits decided
    elif len(session_state['questions_asked']) > 0 and session_state['turn_number'] >= (CONST.THRESHOLD_MAX_TURNS * len(session_state['questions_asked'])):
        if len(session_state['questions_asked']) <= CONST.THRESHOLD_TOTAL_NUMBER_OF_QUESTIONS:  
            #discuss whether to keep a list or an int that tells number of questions to be asked
            session_state['bot_dialogue'] = CONST.MAX_TURNS_TRIGGERED_QUESTIONS_REMAIN
            chat_history[-1]['bot_dialogue'] = CONST.MAX_TURNS_TRIGGERED_QUESTIONS_REMAIN
            session_state['next_action'] = 'get_primary_question'
        else:
            session_state['bot_dialogue'] = CONST.MAX_TURNS_TRIGGERED_NO_QUESTIONS_REMAIN
            chat_history[-1]['bot_dialogue'] = CONST.MAX_TURNS_TRIGGERED_NO_QUESTIONS_REMAIN
            session_state['termination'] = True      
            
    # Contiguous guardrail and unacceptable answer check breach check
    elif (len(session_state["questions_asked"]) > 0) and \
        (session_state['contiguous_non_technical_guardrail_count'] >= CONST.THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT or session_state['contiguous_technical_guardrail_count'] >= CONST.THRESHOLD_MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT): 
        if len(session_state['questions_asked']) <= CONST.THRESHOLD_TOTAL_NUMBER_OF_QUESTIONS :
            session_state['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_QUESTIONS_REMAIN
            chat_history[-1]['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_QUESTIONS_REMAIN
            session_state['next_action'] = 'get_primary_question'
        else:                                   
            session_state['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_NO_QUESTIONS_REMAIN
            chat_history[-1]['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_NO_QUESTIONS_REMAIN
            session_state['termination'] = True
    
    # Contiguous guardrail breach although no primary question has been asked yet
    elif (len(session_state['questions_asked']) == 0) and \
        (session_state['contiguous_non_technical_guardrail_count'] >= CONST.THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_NO_PRIMARY_QUESTION_GUARDRAIL_COUNT):
            if session_state['label_class1'] not in ["confirmation"]:
                session_state['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_NO_PRIMARY_QUESTION
                chat_history[-1]['bot_dialogue'] = CONST.GUARDRAIL_TRIGGERED_NO_PRIMARY_QUESTION
            else:
                session_state['bot_dialogue'] = "-"
                chat_history[-1]['bot_dialogue'] = "-"
    
    else:
        logger.info("NO OVERRIDES TRIGGERED >>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [generate_action_overrides] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")


###############################################################################################################################
################################################### PERFORM ACTIONS ###########################################################
###############################################################################################################################

async def perform_actions(session_state, chat_history, assessment):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [perform_actions] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    if(session_state['next_action'] == "terminate_interview_confirmation"):
        session_state['bot_dialogue'] = CONST.TERMINATION 
        session_state['termination']=True
    
    elif(session_state['next_action'] == 'get_primary_question'):
        
        # should take a list as parameter and check whether these lists of questions are already asked in the database
        
        
        ### if the questions_asked id list is empty; implies the demand for first primary question; 
        ### no new assessment record needs to be appended to the assessment because the first is initialized in the initialize/ end-point; assessment => [ {assessment_record_1} ]
        if len(session_state['questions_asked']) == 0:
            question_metadata=await get_random_question_metadata(session_state['complexity'], session_state['questions_asked']) 

            helper.pretty_log("DB fetched question_metadata:", question_metadata)
            ### untoggle this comment block for fetching random ####################
            question=question_metadata['question']
            question_id = question_metadata['question_id']  
            session_state['questions_asked'].append(question_id)    # reinitialize the question_id for the new question
            session_state['primary_question'] = question    # reinitialize the primary question
            session_state['question_id'] = question_id    # set the question_id in session state (field was added relatively later)
            session_state['bot_dialogue'] = session_state['bot_dialogue'] + question    # set bot dialogue in session state with the new question
            chat_history[-1]['bot_dialogue'] = session_state['bot_dialogue'] + question   # set bot dialogue in chat history with the new question 
            chat_history[-1]['question_id'] = question_id   # update the chat history with the question id  
            ############################# END HERE ##################################

            # question_id = 1
            # session_state['questions_asked'].append(1)    # reinitialize the question_id for the new question
            # session_state['primary_question'] = "Find an index in an array where the sum of elements to the left equals the sum to the right."    # reinitialize the primary question
            # session_state['bot_dialogue'] = session_state['bot_dialogue'] + "Find an index in an array where the sum of elements to the left equals the sum to the right."    # # set bot dialogue in session state with the new question
            # chat_history[-1]['bot_dialogue'] = session_state['bot_dialogue'] + "Find an index in an array where the sum of elements to the left equals the sum to the right."    # set bot dialogue in chat history with the new question
            # session_state['question_id'] = 1    # set the question_id in session state (field was added relatively later)
            # chat_history[-1]['question_id'] = 1   # update the chat history with the question id  
        else:
            ### fetch a new random question, prepare a new assessment record and append it to assessment list
            question_metadata=await get_random_question_metadata(session_state['complexity'], session_state['questions_asked']) 

            helper.pretty_log("DB fetched question_metadata:", question_metadata)
            question=question_metadata['question']
            question_id = question_metadata['question_id']  
            session_state['questions_asked'].append(question_id)    # reinitialize the question_id for the new question
            session_state['primary_question'] = question    # reinitialize the primary question
            if session_state['contiguous_technical_guardrail_count'] >= CONST.THRESHOLD_MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT or \
                    session_state['contiguous_non_technical_guardrail_count'] >= CONST.THRESHOLD_MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT:
                session_state['bot_dialogue'] = session_state['bot_dialogue'] + question    # set bot dialogue in session_state with the new question
                chat_history[-1]['bot_dialogue'] = session_state['bot_dialogue'] + question   # set bot dialogue in chat history with the new question 
            else:
                session_state['bot_dialogue'] = question    # set bot dialogue in session_state with the new question
                chat_history[-1]['bot_dialogue'] = question   # set bot dialogue in chat history with the new question
            
            session_state['question_id'] = question_id    # set the question_id in session state (field was added relatively later)
            chat_history[-1]['question_id'] = question_id   # update the chat history with the question id 

            ### PREPARING A NEW ASSESSMENT RECORD ###################################
            assessment_payload = helper.get_assessment_payload() 
            assessment_record = {'interview_id':session_state['interview_id'], 'question_id': question_id, 'primary_question_score': CONST.DEF_PRIMARY_QUESTION_SCORE, 'assessment_payload': assessment_payload }
            assessment.append(assessment_record)
        
        # set the next_action flag to be "Pass" again
        session_state['next_action'] = "Pass"

    else:
        logger.info(f"session_state -> next_action FLAG: {session_state['next_action']}")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    # elif len(session_state['questions_asked']) >= CONST.THRESHOLD_TOTAL_NUMBER_OF_QUESTIONS :
    #     session_state['termination'] = True
    #     session_state['bot_dialogue'] = CONST.ALL_QUESTIONS_ANSWERED
    
    # else:
    #     session_state['complexity'] -= 1 #atm questions will become easier since we are not giving another question when candidate is done answering the question
    #     question_metadata = await get_random_question_metadata(session_state['complexity'], session_state['questions_asked']) # should take a list as parameter and check whether these lists of questions are already asked in the database
    #     question=question_metadata['question']
    #     question_id = question_metadata['question_id']
    #     session_state['questions_asked'].append(question_id)

    #     session_state['current_question'] = question
    #     session_state['bot_dialogue'] = session_state['bot_dialogue'] + session_state['current_question']

    #     assessment_payload = get_assessment_payload() #used for initializing assessement_payload for a new question
    #     assessment_payload_record.add_record(session_state['interview_id'], session_state['questions_asked'][-1], assessment_payload['final_score'], assessment_payload)
    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [perform_actions] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")



def log_data(candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_rationale, candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale, assessment_payload_record, assessment_payload_rationale, bot_dialogue_subcriterion ,candidate_dialogue_label, session_state, candidate_dialogue_rationale):
    
    log_file = "rationale_logs.txt"

    log_entry = f"#### ************ CONVERSATION TURN {session_state['turn_number']} ************\n"

    log_entry += f"**ORIGINAL CANDIDATE DIALOGUE:** {candidate_dialogue}\n"
    log_entry += f"**DISTILLED CANDIDATE DIALOGUE:** {distilled_candidate_dialogue}\n"
    log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL:** {candidate_dialogue_label}\n"
    log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL RATIONALE:** {candidate_dialogue_rationale}\n\n"


    if candidate_dialogue_label not in CONST.TECHNICAL_LABELS:
        log_entry += f"**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
        log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
    else:
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II:** {candidate_technical_dialogue_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II RATIONALE:** {candidate_technical_dialogue_classification_rationale}\n\n"
        
        if candidate_technical_dialogue_label  in CONST.TECHNICAL_LABELS_TO_BE_EVALUATED:
            log_entry += "**ANSWER EVALUATION**\n"
            assessment_payload = assessment_payload_record.return_assessment_payload(session_state['interview_id'],session_state['questions_asked'][-1])
            log_entry += f"\n **ASSESSMENT_PAYLOAD:** {assessment_payload} \n"
            log_entry += f"\n**ANSWER EVALUATION RATIONALE:** {assessment_payload_rationale} \n"
            log_entry += f"\n**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
            log_entry += f"\n**SUBCRITERION:** {bot_dialogue_subcriterion}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
        else:
            log_entry += f"**NOHA DIALOGUE:** {session_state['bot_dialogue']}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
    log_entry += f"**ACTION FLAG:** {session_state['next_action']}\n\n"

    # Append log entry with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry_with_timestamp = f"{timestamp}\n{log_entry}\n"

    # Write to file
    with open(log_file, "a") as file:
        file.write(log_entry_with_timestamp)



###############################################################################################################################
################################################### GET NEXT RESPONSE #########################################################
###############################################################################################################################

async def get_next_response(session_state, chat_history, assessment):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [get_next_response] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    
    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)
    # helper.pretty_log("assessment", assessment)
    
    #### ENABLE THE VALIDATE_INPUT() LATER IF REQUIRED
    #### validate_input(session_state, chat_history_record, assessment_payload_record) #used for validating inputs received in get_next_response

    
    candidate_dialogue_rationale = await classify_candidate_dialogue(session_state, chat_history)

    bot_dialogue = session_state['bot_dialogue']
    distilled_candidate_dialogue = session_state['distilled_candidate_dialogue']
    write_to_report (bot_dialogue)
    write_to_report (distilled_candidate_dialogue)
    write_to_report (candidate_dialogue_rationale)
    write_to_report ("-------------------------------")

    # post verification in case technical solution is given for a non-existent question
    if not session_state['question_id'] and session_state['label_class1'] in CONST.TECHNICAL_LABELS:
        session_state['label_class1'] = 'irrelevant' # overwrite the label to be 'irrelevant' and rationale too as below
        candidate_dialogue_rationale = "Candidate has given a technical response although no question has even been asked yet"

    if session_state["label_class1"] in CONST.TECHNICAL_LABELS:
        
        logger.info("Candidate dialogue label '%s' is in TECHNICAL_LABELS. Processing as technical dialogue.", session_state["label_class1"])

        (
            bot_dialogue_rationale, 
            bot_dialogue_causal_subcriterion
        ) = await process_technical(session_state, chat_history, assessment)

    elif session_state["label_class1"] in CONST.NON_TECHNICAL_LABELS:

        logger.info("Candidate dialogue label '%s' is not technical. Processing as non-technical dialogue.", session_state['label_class1'])
        (
            bot_dialogue_rationale, 
            bot_dialogue_causal_subcriterion
        ) = await process_non_technical(session_state, chat_history, assessment, candidate_dialogue_rationale)

    else:
        logger.info("Candidate dialogue label '%s' is neither technical nor non-technical.", session_state['label_class1'])

    await generate_action_overrides(session_state, chat_history, assessment)
    await perform_actions(session_state, chat_history, assessment)

    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [get_next_response] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

    return session_state, chat_history, assessment


# async def get_next_response_old(candidate_dialogue, session_state, chat_history, assessment_payload_record):
    
#     validate_input(candidate_dialogue, session_state, chat_history, assessment_payload_record) #used for validating inputs received in get_next_response
    
#     logger.info("############################################################################################################")
#     logger.info(f"USER INPUT AFTER ENTERING get_next_response FOR TURN {session_state['turn_number']} :\n {candidate_dialogue}")
#     logger.info(f"SESSION STATE RECEIVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {session_state}")
#     logger.info(f"USER CHAT HISTORY RECEIVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {chat_history}")
#     logger.info(f"ASSESSMENT PAYLOAD RECORD RECEIVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {assessment_payload_record}")

#     candidate_dialogue_label, candidate_dialogue_rationale, distilled_candidate_dialogue = await classify_candidate_dialogue(session_state['bot_dialogue'], candidate_dialogue, chat_history.filtered_chat_history(session_state['interview_id'], None))


#     logger.info(f"get_next_response(): Candidate Dialogue Label: {candidate_dialogue_label}")
#     logger.info(f"get_next_response(): Candidate Dialogue Rationale: {candidate_dialogue_rationale}")
#     logger.info(f"get_next_response: Distilled Candidate Dialogue: {distilled_candidate_dialogue}")
    

#     logger.info(f"Checking questions_asked length: {len(session_state['questions_asked'])}")

#     if len(session_state['questions_asked']) == 0:
#         logger.info("No questions have been asked yet.")
        
#         if candidate_dialogue_label == 'confirmation':
#             logger.info("Candidate dialogue label is 'confirmation'. Performing actions...")
#             session_state, assessment_payload_record = await perform_actions(session_state, assessment_payload_record)
            
#             logger.info(f"Updated session_state after actions: {session_state}")
#             chat_history.add_record(
#                 session_state['interview_id'], 
#                 session_state['questions_asked'][-1], 
#                 session_state['bot_dialogue_type'], 
#                 session_state['bot_dialogue'], 
#                 candidate_dialogue, 
#                 distilled_candidate_dialogue
#             )
#             logger.info("Added record to chat history after confirmation.")
#         else:
#             logger.info("Candidate dialogue label is not 'confirmation'. Adding record with question_id as None.")
#             chat_history.add_record(
#                 session_state['interview_id'], 
#                 None, 
#                 session_state['bot_dialogue_type'], 
#                 session_state['bot_dialogue'], 
#                 candidate_dialogue, 
#                 distilled_candidate_dialogue
#             )
        
#         session_state['turn_number'] += 1
#         logger.info(f"Turn number incremented: {session_state['turn_number']}")
#     else:
#         logger.info(f"Questions have been asked. Last question ID: {session_state['questions_asked'][-1]}")

#         chat_history.add_record(
#             session_state['interview_id'], 
#             session_state['questions_asked'][-1], 
#             session_state['bot_dialogue_type'], 
#             session_state['bot_dialogue'], 
#             candidate_dialogue, 
#             distilled_candidate_dialogue
#         )
#         logger.info("Added record to chat history for an existing question.")

#         filtered_chat_history = chat_history.filtered_chat_history(session_state['interview_id'], session_state['questions_asked'][-1])
#         logger.info(f"Filtered chat history retrieved for interview ID {session_state['interview_id']}.")

#         if candidate_dialogue_label in CONST.TECHNICAL_LABELS:
#             logger.info(f"Candidate dialogue label '{candidate_dialogue_label}' is in TECHNICAL_LABELS. Processing as technical dialogue.")
#             (
#                 candidate_technical_dialogue_label, 
#                 candidate_technical_dialogue_classification_rationale,  
#                 bot_dialogue_rationale, 
#                 bot_dialogue_subcriterion, 
#                 assessment_payload_rationale, 
#                 session_state, 
#                 assessment_payload_record
#             ) = await process_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record)

#             logger.info(f"Processed technical dialogue. Label: {candidate_technical_dialogue_label}, Rationale: {candidate_technical_dialogue_classification_rationale}")
#         else:
#             logger.info(f"Candidate dialogue label '{candidate_dialogue_label}' is not technical. Processing as non-technical dialogue.")
#             (
#                 bot_dialogue_rationale, 
#                 bot_dialogue_subcriterion, 
#                 session_state
#             ) = await process_non_technical(distilled_candidate_dialogue, session_state, filtered_chat_history, assessment_payload_record, candidate_dialogue_label)

#             candidate_technical_dialogue_label = "None"
#             candidate_technical_dialogue_classification_rationale = "None"
#             assessment_payload_rationale = "None"
#             logger.info("Non-technical processing completed. Assigned 'None' values for missing technical fields.")

#         session_state, assessment_payload_record = await generate_action_overrides(session_state, assessment_payload_record)
#         logger.info("Generated action overrides.")

#     # logger.info(f"Final session_state: {session_state}")

        
#         session_state, assessment_payload_record = await perform_actions(session_state, assessment_payload_record)
#         log_data(candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_rationale, candidate_technical_dialogue_label, candidate_technical_dialogue_classification_rationale, assessment_payload_record, assessment_payload_rationale, bot_dialogue_subcriterion ,candidate_dialogue_label, session_state, candidate_dialogue_rationale) # toggle on/off if you want data to be logged
        
#     logger.info(f"SESSION STATE BEFORE EXITING FROM get_next_response FOR TURN {session_state['turn_number']} \n {session_state}")
#     return session_state['bot_dialogue'] , session_state, chat_history, assessment_payload_record

