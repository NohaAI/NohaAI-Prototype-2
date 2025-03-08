from src.utils import logger
from src.services.llm import llm_service
import json
from src.services.llm.prompts.classify_candidate_dialogue_prompt import classify_candidate_dialogue_prompt_template
logger = logger.get_logger(__name__)

async def classify_candidate_dialogue(session_state, chat_history):
    logger.info("\n\n\n>>>>>>>>>>>FUNCTION [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>")

    classify_candidate_dialogue_prompt=classify_candidate_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    classify_candidate_dialogue_chain=(classify_candidate_dialogue_prompt|llm_model)

    llm_inputs = {'bot_dialogue': session_state["bot_dialogue"],
                'candidate_dialogue': session_state["candidate_dialogue"],
                'chat_history': chat_history,
                'distilled_candidate_dialogue': chat_history["distilled_candidate_dialogue"] 
                }

    classification_response = await classify_candidate_dialogue_chain.ainvoke(llm_inputs)
    classification_content = json.loads(classification_response.content)

    logger.info(f"\nOUTPUTS FROM CLASSIFY CANDIDATE DIALOGUE LLM : {classification_content} \n")
   
    label_class1 = classification_content[0]
    rationale = classification_content[1]
    distilled_candidate_dialogue = classification_content[2]

     # update the respective fields in the session_state and chat_history
    session_state['candidate_dialogue'] = distilled_candidate_dialogue  # replaces the original candidate_dialogue with the refined version to carry forward hereafter
    chat_history[-1]['distilled_candidate_dialogue'] = distilled_candidate_dialogue # adds the distilled version for update in DB to the recentmost dict record in the chat_history list

    logger.info(">>>>>>>>>>>FUNCTION EXIT [classify_candidate_dialogue] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return label_class1, rationale, distilled_dialogue #where 0, 1, 2 are label, rationale and distilled dialoguer respectively     
