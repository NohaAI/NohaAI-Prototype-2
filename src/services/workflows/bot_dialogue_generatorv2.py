from src.utils.logger import get_logger
from src.services.llm import llm_service
import json
from src.services.llm.prompts.bot_dialogue_prompt import bot_dialogue_prompt_template 
# Initialize logger
logger = get_logger(__name__)

async def generate_dialogue(class_label, distilled_chat_history, candidate_dialogue, question, answer_evaluation=None,  bot_dialogue=None, rationale=None):
    # non_technical_class_labels=["illegible", "irrelevant", "clarification(specific)", "clarification(open)", "request(guidance)", "request(termination)", "request(proceed)", "request(break)", "disregard", "illegitimate", "uncertainty"]
    if not  bot_dialogue:
         bot_dialogue=""
    if not rationale:
        rationale=""
    if not answer_evaluation:
        answer_evaluation={}
   #writing to rationale_logs.txt
    # generate_dialogue_inputs=f"GENERATE DIALOGUE INPUTS class_label : {class_label} , candidate_dialogue : {candidate_dialogue}, question : {question}, previous_dalogue : { bot_dialogue} rationale : {rationale} \n"
    # log_file = "rationale_logs.txt"
    # with open(log_file, "a") as file:
    #     file.write(generate_dialogue_inputs)
    
    bot_dialogue_prompt=bot_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model()
    bot_dialogue_prompt_chain=(bot_dialogue_prompt|llm_model)
    
    llm_inputs = {'class': class_label, 
                'tech_question': question,
                'bot_dialogue':  bot_dialogue,
                'candidate_dialogue': candidate_dialogue,
                'chat_history' : distilled_chat_history,
                'rationale': rationale,
                'answer_evaluation' : answer_evaluation
                }

    bot_dialogue_generator_response=await bot_dialogue_prompt_chain.ainvoke(llm_inputs)
    
    bot_dialogue_generator_fallbacks = {"rationale": "LLM DIDNT GENERATE RATIONALE", "next_action": "Pass", "subcriterion": "LLM DIDNT PROVIDE SUBCRITERION"}
    
    bot_dialogue_generator_content=json.loads(bot_dialogue_generator_response.content)
    for key, value in bot_dialogue_generator_fallbacks.items():
        if key not in bot_dialogue_generator_content:
            bot_dialogue_generator_content[key] = value
    dialogue=bot_dialogue_generator_content['response']
    rationale=bot_dialogue_generator_content['rationale']
    subcriterion=bot_dialogue_generator_content['subcriterion']
    next_action=bot_dialogue_generator_content['next_action']
    return dialogue, rationale, subcriterion, next_action

