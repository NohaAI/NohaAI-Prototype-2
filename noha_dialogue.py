from datetime import datetime
import asyncio
import json
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from src.services.workflows.answer_evaluator import evaluate_answer
from src.dao.question import get_question_metadata
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.services.workflows.bot_dialogue_generatorv2 import generate_dialogue 
from src.dao.chat_history import batch_insert_chat_history
from src.services.workflows.answer_classifer import classify_candidate_answer
from src.dao.interview_question_evaluation import add_question_evaluation
from src.dao.interview_session_state import get_interview_session_state,add_interview_session_state,update_interview_session_state,delete_interview_session_state
from src.utils.logger import get_logger
# async def async_get_bot_dialogue(user_input, session_state):
#     return await get_bot_dialogue(user_input, session_state)

logger = get_logger(__name__)

def run_async(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func)


async def get_noha_dialogue(user_input, session_state):
    interview_thresholds = {
    "MAX_TURNS": 10,
    "SCORE_THRESHOLD": 5,
    "MAX_CONTIGUOUS_GUARDRAIL_COUNT": 4,
    "MAX_GUARDRAIL_COUNT": 10,
    "MAX_CONTIGUOUS_UNACCEPTABLE_ANSWER_COUNT": 4
    }
    logger.info("############################################################################################################")
    logger.info(f"USER AFTER ENTERING get_noha_dialogue LOADING : {user_input}")
    logger.info(f"SESSION STATE LOADED IN get_noha_dialogue FOR TURN {session_state['conversation_turn']} :\n {session_state}")
    if isinstance(session_state['meta_payload'], dict):
        session_state["meta_payload"] = EvaluateAnswerRequest(**session_state["meta_payload"])
    original_user_input = user_input
    if(session_state['turn'] == 1):
        session_state['messages'].append({"role": "user", "content" : user_input})
        if session_state['previous_bot_dialogue'] == session_state['current_question']:
            session_state['chat_history'].append({"technical": session_state['previous_bot_dialogue'],"answer": user_input})
        else:
            session_state['chat_history'].append({"reciprocation": session_state['previous_bot_dialogue'],"answer": user_input})

        classify_candidate_dialogue_response=await classify_candidate_dialogue(session_state['current_question'], user_input, session_state['chat_history'])
        classify_candidate_dialogue_content=json.loads(classify_candidate_dialogue_response.content)
        candidate_dialogue_label=classify_candidate_dialogue_content[0]
        candidate_dialogue_rationale=classify_candidate_dialogue_content[1]
        user_input=classify_candidate_dialogue_content[2]
        technical_labels=['technical', 'clarification(specific)']
        contiguous_guardrail_labels=['clarification(open)', 'uncertainty', 'inability']
        if candidate_dialogue_label in contiguous_guardrail_labels:
            session_state['contigous_guardrails_count']+=1
        if candidate_dialogue_label not in technical_labels:
            
            print(f"CAME INSIDE GENERATE DIALOGUE TRY BLOCK FOR TURN {session_state['conversation_turn']}")
            logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']} CANDIDATE DIALOGUE LABEL : {candidate_dialogue_label} \n CHAT HISTORY : {session_state['chat_history']}\n USER INPUT : {user_input} \n CURRENT QUESTION : {session_state['current_question']} \n ASSESSMENT PAYLOAD : {session_state['assessment_payload']} \n ")

            bot_dialogue_generator_response=await generate_dialogue(candidate_dialogue_label, session_state['chat_history'], user_input, session_state['current_question'], session_state['hint_count'], session_state['assessment_payload'],None,None)
           
            bot_dialogue_generator_content=json.loads(bot_dialogue_generator_response.content)

            bot_dialogue_generator_fallbacks = {"rationale": "LLM DIDNT GENERATE RATIONALE","action_flag": "Pass","subcriterion": "LLM DIDNT GENERATE SUBCRITERION"}
            for key, value in bot_dialogue_generator_fallbacks.items():
                if key not in bot_dialogue_generator_content:
                    bot_dialogue_generator_content[key] = value
            bot_dialogue = bot_dialogue_generator_content['response']
            bot_dialogue_rationale = bot_dialogue_rationale['rationale']
            session_state['action_flag'] = bot_dialogue_generator_content['action_flag']
            
            print(f"EXITED GENERATE DIALOGUE TRY BLOCK FOR TURN {session_state['conversation_turn']}")
            session_state['previous_bot_dialogue']=bot_dialogue
            session_state['messages'].append({"role": "bot", "content": bot_dialogue})
            session_state['conversation_turn'] += 1 
        else:
            session_state['contigous_guardrails_count'] = 0
            candidate_answer_classification_response = await classify_candidate_answer(session_state['meta_payload'].question, user_input, session_state['chat_history'])
            candidate_answer_classification_content = json.loads(candidate_answer_classification_response.content)
            candidate_answer_label = candidate_answer_classification_content[0]
            candidate_answer_classification_rationale = candidate_answer_classification_content[1]
            candidate_answer_labels_not_tobe_evaluated=['doubt(concept)']
            if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
                session_state['meta_payload'].answer = user_input
                
                print(f"CAME INSIDE ANSWER EVALUATOR FOR TURN {session_state['conversation_turn']}")
                answer_evaluation_response = await evaluate_answer(session_state['meta_payload'], session_state['chat_history'])
                assessment_payload = answer_evaluation_response[0] #answer evaluation
                assessment_payload_rationale=answer_evaluation_response[1] #answer evaluation rationale
                session_state['assessment_payload']=assessment_payload
                session_state['meta_payload'].eval_distribution = assessment_payload['criteria_scores']
                session_state['eval_distribution'] = assessment_payload['criteria_scores']
                session_state['final_score'] = round(assessment_payload['final_score'],2)
                session_state['turn'] += 1
                  
            else:
                session_state['contiguous_unacceptable_answer_count'] +=1 
            # session_state['turn'] += 1
            print(f"EXITED ANSWER EVALUATOR FOR TURN {session_state['conversation_turn']}")
            session_state['conversation_turn'] +=1
           
            print(f"CAME INSIDE BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']}")

            logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']} CANDIDATE DIALOGUE LABEL : {candidate_answer_label} \n CHAT HISTORY : {session_state['chat_history']}\n USER INPUT : {user_input} \n CURRENT QUESTION : {session_state['current_question']} \n ASSESSMENT PAYLOAD : {session_state['assessment_payload']} \n BOT DIALOGUE : {session_state['meta_payload'].question} \n CANDIDATE ANSWER CLASSIFICATION RATIONALE : {candidate_answer_classification_rationale} \n")

            bot_dialogue_generator_response=await generate_dialogue(candidate_answer_label, session_state['chat_history'], user_input,session_state['current_question'], session_state['hint_count'], session_state['assessment_payload'], session_state['meta_payload'].question,candidate_answer_classification_rationale)
            
            bot_dialogue_generator_content=json.loads(bot_dialogue_generator_response.content)
            bot_dialogue_generator_fallbacks = {"rationale": "LLM DIDNT GENERATE RATIONALE","action_flag": "Pass","subcriterion": "LLM DIDNT GENERATE SUBCRITERION"}
            for key, value in bot_dialogue_generator_fallbacks.items():
                if key not in bot_dialogue_generator_content:
                    bot_dialogue_generator_content[key] = value
            bot_dialogue=bot_dialogue_generator_content['response']
            bot_dialogue_rationale=bot_dialogue_generator_content['rationale']
            bot_dialogue_subcriterion=bot_dialogue_generator_content['subcriterion']
            session_state['action_flag']=bot_dialogue_generator_content['action_flag']

            print(f"EXITED BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']}")
            session_state['previous_bot_dialogue']=bot_dialogue
            session_state['meta_payload'].question = bot_dialogue
            session_state['messages'].append({"role": "bot", "content": bot_dialogue})
    
    else:
        session_state['messages'].append({"role": "user", "content" : user_input})
        if session_state['previous_bot_dialogue'] == session_state['meta_payload'].question:
            session_state['chat_history'].append({"hint": session_state['previous_bot_dialogue'],"answer": user_input})
        else:
            session_state['chat_history'].append({"reciprocation": session_state['previous_bot_dialogue'],"answer": user_input})

        classify_candidate_dialogue_response=await classify_candidate_dialogue(session_state['meta_payload'].question, user_input, session_state['chat_history'])
        classify_candidate_dialogue_content=json.loads(classify_candidate_dialogue_response.content)
        candidate_dialogue_label=classify_candidate_dialogue_content[0]
        candidate_dialogue_rationale=classify_candidate_dialogue_content[1]
        user_input=classify_candidate_dialogue_content[2]
        technical_labels=['technical', 'clarification(specific)']
        contiguous_guardrail_labels=['clarification(open)', 'uncertainty', 'inability']
        if candidate_dialogue_label in contiguous_guardrail_labels:
            session_state['contigous_guardrails_count']+=1
        if candidate_dialogue_label not in technical_labels:
            print(f"ENTERED BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']}")

            logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']} \n CLASS LABEL : {candidate_dialogue_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['meta_payload'].question} \n CANDIDATE DIALOGUE : {user_input} \n CHAT HISTORY : {session_state['chat_history']} \n  ASSESSMENT PAYLOAD : {session_state['assessment_payload']} ")

            bot_dialogue_generator_response=await generate_dialogue(candidate_dialogue_label, session_state['chat_history'], user_input, session_state['current_question'], session_state['hint_count'], session_state['assessment_payload'],session_state['meta_payload'].question,None)
            bot_dialogue_generator_content=json.loads(bot_dialogue_generator_response.content)
            bot_dialogue_generator_fallbacks = {"rationale": "LLM DIDNT GENERATE RATIONALE","action_flag": "Pass","subcriterion": "LLM DIDNT GENERATE SUBCRITERION"}
            for key, value in bot_dialogue_generator_fallbacks.items():
                if key not in bot_dialogue_generator_content:
                    bot_dialogue_generator_content[key] = value
            bot_dialogue=bot_dialogue_generator_content['response']
            bot_dialogue_rationale=bot_dialogue_generator_content['rationale']
            session_state['action_flag']=bot_dialogue_generator_content['action_flag']
           
            print(f"EXITED BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']}")

            session_state['previous_bot_dialogue']=bot_dialogue
            session_state['messages'].append({"role": "bot", "content": bot_dialogue})
            session_state['turn'] += 1 
            session_state['conversation_turn'] += 1 
        else:
            session_state['contigous_guardrails_count'] = 0
            candidate_answer_classification_response = await classify_candidate_answer(session_state['meta_payload'].question, user_input, session_state['chat_history'])
            candidate_answer_classification_content = json.loads(candidate_answer_classification_response.content)
            candidate_answer_label = candidate_answer_classification_content[0]
            candidate_answer_classification_rationale = candidate_answer_classification_content[1]
            candidate_answer_labels_not_tobe_evaluated=['doubt(concept)']
            if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
                session_state['meta_payload'].answer = user_input
                
                print(f"ENTERED EVALUATE ANSWER FOR TURN {session_state['conversation_turn']}")
                answer_evaluation_response = await evaluate_answer(session_state['meta_payload'], session_state['chat_history'],session_state['assessment_payload']['evaluation_results'])
                assessment_payload = answer_evaluation_response[0] #answer evaluation
                assessment_payload_rationale=answer_evaluation_response[1] #answer evaluation rationale
                session_state['assessment_payload']=assessment_payload
                session_state['meta_payload'].eval_distribution = assessment_payload['criteria_scores']
                session_state['eval_distribution'] = assessment_payload['criteria_scores']
                session_state['final_score'] = round(assessment_payload['final_score'],2)
                print(f"EXITED EVALUATE ANSWER FOR TURN {session_state['conversation_turn']}")
            else:
                session_state['contiguous_unacceptable_answer_count'] +=1 
            session_state['turn'] += 1
            session_state['conversation_turn'] +=1
           
            print(f"ENTERED GENERATE DIALOGUE TRY BLOCK {session_state['conversation_turn']}")

            logger.info(f"INPUTS TO BOT DIALOGUE GENERATOR FOR TURN {session_state['conversation_turn']} \n CLASS LABEL : {candidate_answer_label}\n  TECH QUESTION : {session_state['current_question']}\n BOT DIALOGUE : {session_state['meta_payload'].question} \n CANDIDATE DIALOGUE : {user_input} \n CHAT HISTORY : {session_state['chat_history']} \n CANDIDATE ANSWER CLASSIFICATION RATIONALE : {candidate_answer_classification_rationale} \n ASSESSMENT PAYLOAD : {session_state['assessment_payload']} ")

            bot_dialogue_generator_response=await generate_dialogue(candidate_answer_label, session_state['chat_history'], user_input,session_state['current_question'], session_state['hint_count'], session_state['assessment_payload'], session_state['meta_payload'].question, candidate_answer_classification_rationale)
            bot_dialogue_generator_fallbacks = {"rationale": "LLM DIDNT GENERATE RATIONALE","action_flag": "Pass","subcriterion": "LLM DIDNT GENERATE SUBCRITERION"}
            bot_dialogue_generator_content=json.loads(bot_dialogue_generator_response.content)
            for key, value in bot_dialogue_generator_fallbacks.items():
                if key not in bot_dialogue_generator_content:
                    bot_dialogue_generator_content[key] = value
            bot_dialogue=bot_dialogue_generator_content['response']
            bot_dialogue_rationale=bot_dialogue_generator_content['rationale']
            bot_dialogue_subcriterion=bot_dialogue_generator_content['subcriterion']
            session_state['action_flag']=bot_dialogue_generator_content['action_flag']
               
            print(f"EXITED GENERATE DIALOGUE TRY BLOCK {session_state['conversation_turn']}")
            
            session_state['previous_bot_dialogue']=bot_dialogue
              
            session_state['meta_payload'].question = bot_dialogue
            session_state['messages'].append({"role": "bot", "content": bot_dialogue})
    
    if(session_state['final_score'] > interview_thresholds['SCORE_THRESHOLD']):
        # if len(session_state['interview_question_list']) != 0:  #to be used for continous questions
        #     bot_dialogue = "Since you have answered this question, let us move on to the next one : "
        #     # bot_dialogue="Since you have solved this question, can you now start writing code for it?"
        #     session_state['action_flag']='get_new_question'
        # else:
        session_state['conclude']=True      
        session_state['conclude_message']="Since you have solved this question, can you now start writing code for it?"
        session_state['meta_payload'].question = session_state['conclude_message']
        session_state['messages'].pop() 
        session_state['messages'].append({"role": "bot", "content": session_state['conclude_message']}) 
    if session_state['conversation_turn'] > (interview_thresholds['MAX_TURNS'] * session_state['number_of_questions']):
        if len(session_state['interview_question_list']) != 0:
            bot_dialogue="So far so good, let us move on to the next question : "
            # bot_dialogue="We appreciate your effort on the problem! Now, can you code it for us? Let us know when you're ready."
            session_state['action_flag']='get_new_question'
        else:
            session_state['conclude']=True      
            session_state['conclude_message']="We appreciate your effort on the problem! Now, can you code it for us? Let us know when you're ready."
            session_state['meta_payload'].question = session_state['conclude_message']
            session_state['messages'].pop() 
            session_state['messages'].append({"role": "bot", "content": session_state['conclude_message']})
            
    if session_state['contigous_guardrails_count']==interview_thresholds['MAX_CONTIGUOUS_GUARDRAIL_COUNT'] or session_state['contiguous_unacceptable_answer_count'] > interview_thresholds['MAX_CONTIGUOUS_UNACCEPTABLE_ANSWER_COUNT']:
        if len(session_state['interview_question_list']) != 0:
            session_state['action_flag']='get_new_question'
            bot_dialogue="It seems there is a lack of clarity. Let us move on to the next question : "
        else:    
            session_state['conclude']=True
            session_state['conclude_message']="It seems there is a lack of clarity. Let us conclude here."
            session_state['meta_payload'].question = session_state['conclude_message']
            session_state['messages'].append({"role": "bot", "content": session_state['conclude_message']})

    if("turn" in session_state and session_state['action_flag'] == 'get_new_question'):
        if(len(session_state['interview_question_list']) == 0):
            session_state['conclude']=True
            session_state['conclude_message']="You have exhausted all questions in this interview"
            bot_dialogue=session_state['conclude_message']
            session_state['meta_payload'].question = session_state['conclude_message']
            session_state['messages'].pop()
            session_state['messages'].append({"role": "bot", "content": session_state['conclude_message']})
        else:
            await add_question_evaluation(session_state['meta_payload'].interview_id, session_state['meta_payload'].question_id, session_state['final_score'], json.dumps(session_state['assessment_payload']))
            await batch_insert_chat_history(session_state['meta_payload'].interview_id, session_state['meta_payload'].question_id,session_state['chat_history'])
            #add answer eval and chat history for this question to DB
            session_state['chat_history'].clear()
            #there should be logic for question switching right now a list is responsible for question switching
            session_state['meta_payload'].question_id = session_state['interview_question_list'].pop()
            session_state['meta_payload'].eval_distribution = [0, 0, 0, 0, 0, 0, 0]
            session_state['eval_distribution'] = [0, 0, 0, 0, 0, 0, 0]
            session_state['final_score'] = 0
            session_state['number_of_questions']+=1
            next_question_metadata=await get_question_metadata(session_state['meta_payload'].question_id)
            next_question=next_question_metadata['question']
            session_state['current_question']=next_question
            session_state['meta_payload'].question = session_state['current_question']
            bot_dialogue = bot_dialogue + session_state['current_question']
            session_state['messages'].pop()
            session_state['messages'].append({"role": "bot", "content": bot_dialogue})
            session_state['previous_bot_dialogue']=bot_dialogue
            session_state['turn']=1
            #session_state['conversation_turn']=1    
            
    if(session_state['action_flag'] == "terminate_interview_confirmation"):
        session_state['conclude']=True
        await add_question_evaluation(session_state['meta_payload'].interview_id, session_state['meta_payload'].question_id, session_state['final_score'], json.dumps(session_state['assessment_payload']))
        await batch_insert_chat_history(session_state['meta_payload'].interview_id, session_state['meta_payload'].question_id,session_state['chat_history'])
    
    log_file = "rationale_logs.txt"
    class_label = candidate_dialogue_label
    log_entry = f"#### ************ CONVERSATION TURN {session_state['conversation_turn']} ************\n"

    if class_label:
        log_entry += f"**ORIGINAL CANDIDATE DIALOGUE:** {original_user_input}\n"
        log_entry += f"**DISTILLED CANDIDATE DIALOGUE:** {user_input}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL:** {class_label}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL RATIONALE:** {candidate_dialogue_rationale}\n\n"

    log_entry += f"**ACTION FLAG:** {session_state['action_flag']}\n\n"

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

    if isinstance(session_state['meta_payload'], dict):
        session_state['meta_payload'] = EvaluateAnswerRequest(**session_state['meta_payload'])
    logger.info(f"SESSION STATE BEFORE RETURNING FROM get_noha_dialogue FOR TURN {session_state['conversation_turn']} \n {session_state}")
    return [bot_dialogue,session_state]

