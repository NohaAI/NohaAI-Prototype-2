from src.utils import logger
from src.utils import helper as helper
from src.services.llm import llm_service
import json
from src.services.llm.prompts.classify_candidate_dialogue_prompt import classify_candidate_dialogue_prompt_template
logger = logger.get_logger(__name__)

async def classify_candidate_dialogue(session_state, chat_history):
    logger.info("\n\n\n>>>>>>>>>>>FUNCTION [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

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

    helper.pretty_log("CLASSIFY CANDIDATE DIALOGUE LLM OUTPUT", llm_content_candidate_dialogue_classification, 1)
   
    label_class1 = llm_content_candidate_dialogue_classification[0]
    candidate_dialogue_rationale = llm_content_candidate_dialogue_classification[1]
    distilled_candidate_dialogue = llm_content_candidate_dialogue_classification[2]

     # update the respective fields in the session_state and chat_history
    session_state['label_class1'] = label_class1 # updates the classifier 1 label in the session state
    session_state['candidate_dialogue'] = distilled_candidate_dialogue  # replaces the original candidate_dialogue with the refined version to carry forward hereafter
    chat_history[-1]['distilled_candidate_dialogue'] = distilled_candidate_dialogue # adds the distilled version for update in DB to the recentmost dict record in the chat_history list
    session_state['distilled_candidate_dialogue'] = ""

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return candidate_dialogue_rationale
