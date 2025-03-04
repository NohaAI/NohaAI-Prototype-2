import json
from src.utils import logger
from src.services.llm import llm_service
from src.services.llm.prompts.answer_classifier_prompt import classify_candidate_answer_prompt_template
logger = logger.get_logger(__name__)

async def classify_candidate_technical_dialogue(bot_dialogue, candidate_dialogue, distilled_chat_history, question):
    classify_candidate_answer_prompt=classify_candidate_answer_prompt_template() #TODO refactor same as the func above
    llm_model = llm_service.get_openai_model()
    classify_candidate_answer_chain=(classify_candidate_answer_prompt|llm_model)

    llm_inputs={'tech_question': question,
                'bot_dialogue': bot_dialogue,
                'candidate_dialogue': candidate_dialogue,
                'chat_history': distilled_chat_history 
                }

    classification_response=await classify_candidate_answer_chain.ainvoke(llm_inputs)
    classification_content = json.loads(classification_response.content)
    label = classification_content[0]
    rationale = classification_content[1]

    return label, rationale    
