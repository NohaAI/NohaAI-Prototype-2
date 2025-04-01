import src.config.logging_config
from src.utils import logger as LOGGER
from src.config import constants as CONST
from src.config import logging_config as LOGCONF
from src.services.llm import llm_service
from src.services.llm.prompts.classify_candidate_dialogue_prompt import classify_candidate_dialogue_prompt_template
import json

async def classify_candidate_dialogue(session_state, chat_history):
    LOGGER.log_info("\n\n\n>>>>>>>>>>>FUNCTION [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    LOGGER.pretty_log("session_state", session_state, LOGCONF.DEBUG2)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG2)
    LOGGER.pretty_log("session_state['candidate_dialogue']", session_state['candidate_dialogue'])

    classify_candidate_dialogue_prompt=classify_candidate_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    classify_candidate_dialogue_chain=(classify_candidate_dialogue_prompt|llm_model)

    llm_inputs = {'bot_dialogue': session_state["bot_dialogue"],
                'candidate_dialogue': session_state["candidate_dialogue"],
                'chat_history': chat_history,
                'distilled_candidate_dialogue': ""
                }

    llm_response_candidate_dialogue_classification = await classify_candidate_dialogue_chain.ainvoke(llm_inputs)
    llm_content_candidate_dialogue_classification = json.loads(llm_response_candidate_dialogue_classification.content)

    LOGGER.pretty_log("CLASSIFY CANDIDATE DIALOGUE LLM OUTPUT", llm_content_candidate_dialogue_classification, LOGCONF.INFO)
   
    label_class1 = llm_content_candidate_dialogue_classification[0]
    candidate_dialogue_rationale = llm_content_candidate_dialogue_classification[1]
    distilled_candidate_dialogue = llm_content_candidate_dialogue_classification[2]

     # update the respective fields in the session_state and chat_history
    session_state['label_class1'] = label_class1 # updates the classifier 1 label in the session state
    session_state['candidate_dialogue'] = distilled_candidate_dialogue  # replaces the original candidate_dialogue with the refined version to carry forward hereafter
    chat_history[-1]['distilled_candidate_dialogue'] = distilled_candidate_dialogue # adds the distilled version for update in DB to the recentmost dict record in the chat_history list
    session_state['distilled_candidate_dialogue'] = distilled_candidate_dialogue # updates the distilled candidate_dialogue in the session state
    
    LOGGER.pretty_log("session_state['candidate_dialogue']", session_state['candidate_dialogue'])
    LOGGER.pretty_log("session_state['distilled_candidate_dialogue']", session_state['distilled_candidate_dialogue']) 
    LOGGER.pretty_log("session_state['label_class1']", label_class1)
    LOGGER.pretty_log("session_state", session_state, LOGCONF.DEBUG1)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG1)

    LOGGER.log_info("\n\n>>>>>>>>>>>FUNCTION EXIT [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return candidate_dialogue_rationale