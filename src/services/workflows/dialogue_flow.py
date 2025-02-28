from datetime import datetime
import json
from src.schemas.endpoints import EvaluateAnswerRequest
from src.services.workflows.answer_evaluator import evaluate_answer
from src.dao.question import get_question_metadata
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.services.workflows.bot_dialogue_generatorv2 import generate_dialogue 
from src.dao.chat_history import batch_insert_chat_history
from src.services.workflows.answer_classifer import classify_candidate_technical_dialogue
from src.dao.interview_question_evaluation import add_question_evaluation
from src.utils.logger import get_logger
from src.schemas.taxonomy import TECHNICAL_LABELS, TECHNICAL_LABELS_NOT_TO_BE_EVALUATED, TECHNICAL_LABELS_TO_BE_EVALUATED, NON_TECHNICAL_LABELS
from src.services.workflows.interview_thresholds import MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT, MAX_GUARDRAIL_COUNT,MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT,MAX_TURNS,SCORE_THRESHOLD

logger = get_logger(__name__)

async def get_next_response(user_input, session_state, user_chat_history, distilled_chat_history, assessment_payload):
   
    logger.info("############################################################################################################")
    logger.info(f"USER INPUT AFTER ENTERING get_next_response FOR TURN {session_state['turn_number']} :\n {user_input}")
    logger.info(f"SESSION STATE RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {session_state}")
    logger.info(f"DISTILLED CHAT HISTORY RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {distilled_chat_history}")
    logger.info(f"USER CHAT HISTORY RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {user_chat_history}")
    logger.info(f"ASSESSMENT PAYLOAD RECIEVED IN get_next_response FOR TURN {session_state['turn_number']} :\n {assessment_payload}")

    # classify_candidate_dialogue_response=await classify_candidate_dialogue(session_state['bot_dialogue'], user_input, distilled_chat_history)
    
    candidate_dialogue_label, candidate_dialogue_rationale, distilled_candidate_dialogue = await classify_candidate_dialogue(session_state['bot_dialogue'], user_input, distilled_chat_history)
    #ACCOUNT FOR BOT DIALOGUE TYPE IN SESSION STATE
    distilled_chat_history.append({session_state['bot_dialogue_type']: session_state['bot_dialogue'], "answer": distilled_candidate_dialogue})
    user_chat_history.append({session_state['bot_dialogue_type']: session_state['bot_dialogue'], "answer": user_input})
    
    if candidate_dialogue_label in TECHNICAL_LABELS:
        
        session_state['contigous_non_technical_guardrails_count'] = 0
        candidate_answer_label, candidate_answer_classification_rationale = await classify_candidate_technical_dialogue(session_state['bot_dialogue'], distilled_candidate_dialogue, distilled_chat_history) # refactor into candidate tech dialogue
        
        if candidate_answer_label in TECHNICAL_LABELS_TO_BE_EVALUATED:
            logger.info(f"ENTERED EVALUATE ANSWER FOR TURN {session_state['turn_number']}")
            assessment_payload, assessment_payload_rationale = await evaluate_answer(session_state['question_id'], session_state['bot_dialogue'], distilled_candidate_dialogue, distilled_chat_history, assessment_payload)
            # question_id, question, candidate_answer, eval_distribution, distilled_chat_history, prev_eval = None
            logger.info(f"EXITED EVALUATE ANSWER FOR TURN : {session_state['turn_number']}")
        else:
            session_state['contiguous_technical_guardrail_count'] +=1 
        session_state['turn_number'] +=1
    
        logger.info(f"ENTERED GENERATE DIALOGUE : {session_state['turn_number']}")

        logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']} \n CLASS LABEL : {candidate_answer_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['bot_dialogue']} \n CANDIDATE DIALOGUE : {distilled_candidate_dialogue} \n CHAT HISTORY : {distilled_chat_history} \n CANDIDATE ANSWER CLASSIFICATION RATIONALE : {candidate_answer_classification_rationale} \n ASSESSMENT PAYLOAD : {assessment_payload} ")

        bot_dialogue, bot_dialogue_rationale, bot_dialogue_subcriterion, session_state['next_action'] =await generate_dialogue(candidate_answer_label, distilled_chat_history, distilled_candidate_dialogue,session_state['current_question'], assessment_payload, session_state['bot_dialogue'], candidate_answer_classification_rationale)
        session_state['bot_dialogue_type'] = 'follow-up'
        logger.info(f"EXITED GENERATE DIALOGUE FOR {session_state['turn_number']}")
        session_state['bot_dialogue'] = bot_dialogue
    else:
        #TODO : CONTIGUOUS GUARDRAILS SHOULD BE TAKEN CARE OF IN BOT DIALOGUE REFER ABOVE
        
        if candidate_dialogue_label in NON_TECHNICAL_LABELS:
            session_state['contigous_non_technical_guardrails_count']+=1
        logger.info(f"ENTERED BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']}")
        logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']} \n CLASS LABEL : {candidate_dialogue_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['bot_dialogue']} \n CANDIDATE DIALOGUE : {distilled_candidate_dialogue} \n CHAT HISTORY : {distilled_chat_history} \n  ASSESSMENT PAYLOAD : {assessment_payload} ")

        bot_dialogue, bot_dialogue_rationale, but_dialogue_subcriterion, session_state[''] =await generate_dialogue(candidate_dialogue_label, distilled_chat_history, distilled_candidate_dialogue, session_state['current_question']assessment_payload, session_state['bot_dialogue'], None)
        session_state['bot_dialogue_type'] = 'follow-up'
        
        logger.info(f"EXITED BOT DIALOGUE GENERATOR FOR TURN {session_state['turn_number']}")
        session_state['bot_dialogue']=bot_dialogue
        session_state['turn_number'] += 1 

    if(assessment_payload['final_score'] >= SCORE_THRESHOLD):
        session_state['termination'] = True      
        session_state['bot_dialogue'] = "Since you have solved this question, can you now start writing code for it?"
    # Max Conversation turns check
    if session_state['turn_number'] >= (MAX_TURNS * session_state['number_of_questions']):
        if len(session_state['interview_question_list']) != 0: #discuss whether to keep a list or an int that tells number of questions to be asked
            session_state['bot_dialogue'] = "So far so good, let us move on to the next question : "
            session_state['next_action'] = 'get_new_topic'
        else:
            session_state['termination'] = True      
            session_state['bot_dialogue'] = "We appreciate your effort on the problem! Now, can you code it for us? Let us know when you're ready."
            
    # Contiguous guardrail and unacceptable answer check breach check
             
    if session_state['contigous_non_technical_guardrails_count'] >= MAX_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT  or session_state['contiguous_technical_answer_count'] >= MAX_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT: 
        if len(session_state['interview_question_list']) != 0:
            session_state['next_action']='get_new_topic'
            session_state['bot_dialogue']="It seems there is a lack of clarity. Let us move on to the next question : "
        else:                                   
            session_state['termination']=True
            session_state['bot_dialogue']="It seems there is a lack of clarity. Let us conclude here."

    if(session_state['next_action'] == 'get_new_topic'):
        if(len(session_state['interview_question_list']) == 0):
            session_state['conclude'] = True
            session_state['bot_dialogue'] = "You are all done. There are no more questions left in this interview."
        else:
            await add_question_evaluation(session_state['interview_id'], session_state['question_id'], assessment_payload['final_score'], json.dumps(assessment_payload))
            await batch_insert_chat_history(session_state['interview_id'], session_state['question_id'], distilled_chat_history)
            #add answer eval and chat history for this question to DB
            distilled_chat_history.clear()
            session_state['contiguous_non_technical_guardrails_count'] = 0 
            session_state['contiguous_technical_answer_count'] = 0
            session_state['consecutive_termination_requests'] = 0
            #there should be logic for question switching right now a list is responsible for question switching
            session_state['question_id'] = session_state['interview_question_list'].pop() #responsible for assigning next question_id discuss what to do at the moment
            
            session_state['number_of_questions'] += 1
            next_question_metadata=await get_question_metadata(session_state['question_id'])
            next_question=next_question_metadata['question']
            session_state['current_question'] = next_question
            session_state['bot_dialogue'] = session_state['current_question']
            bot_dialogue = bot_dialogue + session_state['current_question']
            session_state['bot_dialogue'] = bot_dialogue
            session_state['bot_dialogue_type'] = 'new_question'
    if(session_state['next_action'] == "terminate_interview_confirmation"):
        session_state['conclude']=True
        await add_question_evaluation(session_state['interview_id'], session_state['question_id'], session_state['final_score'], json.dumps(session_state['assessment_payload']))
        await batch_insert_chat_history(session_state['interview_id'], session_state['question_id'], user_chat_history)
    
    log_file = "rationale_logs.txt"
    class_label = candidate_dialogue_label
    log_entry = f"#### ************ CONVERSATION TURN {session_state['turn_number']} ************\n"

    if class_label:
        log_entry += f"**ORIGINAL CANDIDATE DIALOGUE:** {user_input}\n"
        log_entry += f"**DISTILLED CANDIDATE DIALOGUE:** {distilled_candidate_dialogue}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL:** {class_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL RATIONALE:** {candidate_dialogue_rationale}\n\n"

    log_entry += f"**ACTION FLAG:** {session_state['next_action']}\n\n"

    if class_label not in ['technical', 'clarification(specific)']:
        log_entry += f"**NOHA DIALOGUE:** {bot_dialogue}\n"
        log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
    else:
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II:** {candidate_answer_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL II RATIONALE:** {candidate_answer_classification_rationale}\n\n"
        
        if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
            log_entry += "**ANSWER EVALUATION**\n"
            subcriteria_score_list = []
            
            for idx, dct in enumerate(assessment_payload['evaluation_results']):
                if idx % 3 == 0:
                    log_entry += "\n"
                log_entry += f"\t{dct}\n"
                k = list(dct)[0]
                subcriteria_score_list.append(dct[k])
            
            log_entry += f"\n**ANSWER EVALUATION RATIONALE : ** \n"
            for idx, item in enumerate(assessment_payload_rationale):
                log_entry += f"\t\t\t {idx+1} : {item} \n"
            
            log_entry += f"\n**SUBCRITERIA SCORES:** {subcriteria_score_list}\n"
            log_entry += f"\n**EVALUATION DISTRIBUTION:** {assessment_payload['criteria_scores']}\n"
            log_entry += f"\n**FINAL SCORE:** {session_state['final_score']}\n"
            log_entry += f"\n**NOHA DIALOGUE:** {bot_dialogue}\n"
            log_entry += f"\n**SUBCRITERION:** {bot_dialogue_subcriterion}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"
        else:
            log_entry += f"**NOHA DIALOGUE:** {bot_dialogue}\n"
            log_entry += f"**NOHA DIALOGUE RATIONALE:** {bot_dialogue_rationale}\n"

    # Append log entry with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry_with_timestamp = f"{timestamp}\n{log_entry}\n"

    # Write to file
    with open(log_file, "a") as file:
        file.write(log_entry_with_timestamp)

    logger.info(f"SESSION STATE BEFORE RETURNING FROM get_noha_dialogue FOR TURN {session_state['turn_number']} \n {session_state}")
    return [bot_dialogue , session_state, distilled_chat_history, assessment_payload]

