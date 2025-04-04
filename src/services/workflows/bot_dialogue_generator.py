from src.utils import logger as helper
from src.services.llm import llm_service
from src.config import constants as CONST
import json
from src.services.llm.prompts.bot_dialogue_prompt import bot_dialogue_prompt_template
from src.utils import logger as LOGGER
from src.config import logging_config as LOGCONF

async def generate_dialogue(session_state, chat_history, assessment, rationale=None):
    LOGGER.log_info("\n\n>>>>>>>>>>>FUNCTION [generate dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    
    LOGGER.pretty_log("session_state", session_state)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG1)  
    # non_technical_class_labels=["illegible", "irrelevant", "clarification(specific)", "clarification(open)", "request(guidance)", "request(termination)", "request(proceed)", "request(break)", "disregard", "illegitimate", "uncertainty"]
    if not session_state['solution_classifier_executed']:
        class_label = session_state['label_class1']
    else:
        class_label = session_state['label_class2']

    new_chat_record = {
        "interview_id": session_state['interview_id'],
        "question_id": session_state['question_id'],
        "bot_dialogue_type": CONST.DEF_BOT_DIALOGUE_TYPE,
        "bot_dialogue": None,
        "candidate_dialogue": CONST.DEF_CANDIDATE_DIALOGUE,
        "distilled_candidate_dialogue": CONST.DEF_DISTILLED_CANDIDATE_DIALOGUE
    }
    chat_history.append(new_chat_record)

    bot_dialogue_prompt=bot_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    bot_dialogue_prompt_chain=(bot_dialogue_prompt|llm_model)

    llm_inputs = {'class_label': class_label,
                'primary_question': session_state['primary_question'],
                'bot_dialogue':  session_state['bot_dialogue'],
                'candidate_dialogue': session_state['candidate_dialogue'],
                'chat_history' : chat_history,
                'rationale': rationale,
                'assessment_payload' : assessment[-1]['assessment_payloads'][-1] if assessment else None,
                }

    llm_response_bot_dialogue_generator = await bot_dialogue_prompt_chain.ainvoke(llm_inputs)
    llm_content_bot_dialogue_generator = json.loads(llm_response_bot_dialogue_generator.content)

    helper.pretty_log("CLASSIFY BOT DIALOGUE LLM OUTPUT", llm_content_bot_dialogue_generator, 1)

    bot_dialogue = llm_content_bot_dialogue_generator['response']
    bot_dialogue_rationale = llm_content_bot_dialogue_generator['rationale']
    bot_dialogue_causal_subcriterion = llm_content_bot_dialogue_generator['subcriterion']
    bot_dialogue_next_action = llm_content_bot_dialogue_generator['next_action']
    if not bot_dialogue_causal_subcriterion:
        bot_dialogue_causal_subcriterion = "< No causal sub-criterion identified >"
    # session_state fields update as per prompt objective
    session_state['bot_dialogue'] = bot_dialogue
    chat_history[-1]['bot_dialogue'] = bot_dialogue
    session_state['next_action'] = bot_dialogue_next_action
    session_state['candidate_dialogue'] = None
    session_state['distilled_candidate_dialogue'] = None

    LOGGER.pretty_log("session_state", session_state)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG1)  
    

    LOGGER.log_info("\n\n>>>>>>>>>>>FUNCTION EXIT [bot_dialogue_generator] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return bot_dialogue_rationale, bot_dialogue_causal_subcriterion

