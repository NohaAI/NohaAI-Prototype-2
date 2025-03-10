from src.utils.logger import get_logger
from src.utils import helper as helper
from src.services.llm import llm_service
import json
from src.services.llm.prompts.bot_dialogue_prompt import bot_dialogue_prompt_template 
# Initialize logger
logger = get_logger(__name__)

async def generate_dialogue(session_state, chat_history, assessment, rationale=None):
    logger.info("\n\n>>>>>>>>>>>FUNCTION [generate dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    
    helper.pretty_log("session_state", session_state)
    helper.pretty_log("chat_history", chat_history)
    helper.pretty_log("assessment", assessment)
    # non_technical_class_labels=["illegible", "irrelevant", "clarification(specific)", "clarification(open)", "request(guidance)", "request(termination)", "request(proceed)", "request(break)", "disregard", "illegitimate", "uncertainty"]
    if not session_state['solution_classifier_executed']:
        class_label = session_state['label_class1']
    else:
        class_label = session_state['label_class2']

    bot_dialogue_prompt=bot_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    bot_dialogue_prompt_chain=(bot_dialogue_prompt|llm_model)
    
    llm_inputs = {'class_label': class_label,
                'primary_question': session_state['primary_question'],
                'bot_dialogue':  session_state['bot_dialogue'],
                'candidate_dialogue': session_state['candidate_dialogue'],
                'chat_history' : chat_history,
                'rationale': rationale,
                'assessment_payload' : assessment[-1]['assessment_payload']
                }

    llm_response_bot_dialogue_generator = await bot_dialogue_prompt_chain.ainvoke(llm_inputs)
    llm_content_bot_dialogue_generator = json.loads(llm_response_bot_dialogue_generator.content)

    helper.pretty_log("CLASSIFY BOT DIALOGUE LLM OUTPUT", llm_content_bot_dialogue_generator)

    bot_dialogue = llm_content_bot_dialogue_generator['response']
    bot_dialogue_rationale = llm_content_bot_dialogue_generator['rationale']
    bot_dialogue_causal_subcriterion = llm_content_bot_dialogue_generator['subcriterion']
    bot_dialogue_next_action = llm_content_bot_dialogue_generator['next_action']

    session_state['bot_dialogue'] = bot_dialogue
    session_state['next_action'] = bot_dialogue_next_action

    logger.info(">>>>>>>>>>>FUNCTION EXIT [bot_dialogue_generator] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return bot_dialogue_rationale, bot_dialogue_causal_subcriterion

