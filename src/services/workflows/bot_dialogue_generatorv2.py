from src.utils.logger import get_logger
from src.services.llm import llm_service
import json
from src.services.llm.prompts.bot_dialogue_prompt import bot_dialogue_prompt_template 
# Initialize logger
logger = get_logger(__name__)

async def generate_dialogue(label, chat_history, answer, question, hint_count, answer_evaluation=None, previous_dialogue=None,rationale=None):
    # non_technical_class_labels=["illegible", "irrelevant", "clarification(specific)", "clarification(open)", "request(guidance)", "request(termination)", "request(proceed)", "request(break)", "disregard", "illegitimate", "uncertainty"]

    if not previous_dialogue:
        follow_up_question=""
    if not rationale:
        rationale=""
    if not answer_evaluation:
        answer_evaluation={}
   #writing to rationale_logs.txt
    generate_dialogue_inputs=f"GENERATE DIALOGUE INPUTS label : {label} , answer : {answer}, question : {question}, previous_dalogue : {previous_dialogue} rationale : {rationale} \n"
    log_file = "rationale_logs.txt"
    with open(log_file, "a") as file:
        file.write(generate_dialogue_inputs)
    
    follow_up_question=previous_dialogue
    bot_dialogue_prompt=bot_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    bot_dialogue_prompt_chain=(bot_dialogue_prompt|llm_model)
    bot_dialogue=await bot_dialogue_prompt_chain.ainvoke({'class': label, 'tech_question': question, 'bot_dialogue': follow_up_question, 'candidate_dialogue': answer,'chat_history' : chat_history, 'rationale': rationale, 'answer_evaluation' : answer_evaluation})
    return bot_dialogue

