import json
from src.utils import logger
from src.utils import helper as helper
from src.services.llm import llm_service
from src.services.llm.prompts.classify_candidate_solution_prompt import classify_candidate_solution_prompt_template
logger = logger.get_logger(__name__)

async def classify_candidate_solution(session_state, chat_history):
    logger.info("\n\n\n>>>>>>>>>>>FUNCTION [classify_candidate_solution] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    classify_candidate_solution_prompt=classify_candidate_solution_prompt_template()
    llm_model = llm_service.get_openai_model()
    classify_candidate_solution_chain=(classify_candidate_solution_prompt|llm_model)

    llm_inputs={'primary_question': session_state['primary_question'],
                'bot_dialogue': session_state['bot_dialogue'],
                'candidate_solution': session_state['candidate_dialogue'],
                'chat_history': chat_history
                }

    llm_response_candidate_solution_classification = await classify_candidate_solution_chain.ainvoke(llm_inputs)
    llm_content_candidate_solution_classification = json.loads(llm_response_candidate_solution_classification.content)

    helper.pretty_log("CLASSIFY CANDIDATE SOLUTION LLM OUTPUT", llm_content_candidate_solution_classification, 1)

    label_class2 = llm_content_candidate_solution_classification[0]
    candidate_solution_rationale = llm_content_candidate_solution_classification[1]

    # TODO: For robustness, probably prompt should return a dict instead of a list to verify missing values
   
    # update the respective fields in the session _state and chat_history
    session_state['label_class2'] = label_class2 # updates the classifier 1 label in the session state
    
    helper.pretty_log("session_state", session_state, 1)
    helper.pretty_log("chat_history", chat_history, 1)

    logger.info("\n\n>>>>>>>>>>>FUNCTION EXIT [classify_candidate_solution] >>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

    return label_class2, candidate_solution_rationale
