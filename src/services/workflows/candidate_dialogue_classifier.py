from src.utils import logger
from src.services.llm import llm_service
import json
from src.services.llm.prompts.classify_candidate_dialogue_prompt import classify_candidate_dialogue_prompt_template
logger = logger.get_logger(__name__)

async def classify_candidate_dialogue(bot_dialogue, candidate_dialogue,chat_history):
    classify_candidate_dialogue_prompt=classify_candidate_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    distilled_dialogue = ""
    classify_candidate_dialogue_chain=(classify_candidate_dialogue_prompt|llm_model)
    logger.info(f"INPUTS TO CLASSIFY CANDIDATE DIALOGUE : \n bot_dialogue: {bot_dialogue} \n candidate_dialogue : {candidate_dialogue} \n chat_history : {chat_history} \n distilled_dialogue : {distilled_dialogue}")
    classification_response = await classify_candidate_dialogue_chain.ainvoke({'bot_dialogue': bot_dialogue,'candidate_dialogue': candidate_dialogue, 'chat_history': chat_history,'distilled_dialogue': distilled_dialogue })
    classification_content = json.loads(classification_response.content)
    label = classification_content[0]
    rationale = classification_content[1]
    distilled_dialogue = classification_content[2]
    #TODO keep a if-else or try except to verify LLM Response
    return label, rationale, distilled_dialogue #where 0, 1, 2 are label, rationale and distilled dialoguer respectively     
