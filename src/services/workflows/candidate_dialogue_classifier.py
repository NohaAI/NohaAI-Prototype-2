from fastapi import FastAPI
import uvicorn
from src.utils import logger
from src.services.llm import llm_service
from src.services.llm.prompts.classify_candidate_dialogue_prompt import classify_candidate_dialogue_prompt_template
logger = logger.get_logger(__name__)

app=FastAPI()

@app.get('/classify_candidate_dialogue')
async def classify_candidate_dialogue(bot_dialogue, candidate_dialogue,chat_history):
    classify_candidate_dialogue_prompt=classify_candidate_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    distilled_candidate_dialogue = ""
    classify_candidate_dialogue_chain=(classify_candidate_dialogue_prompt|llm_model)
    candidate_dialogue_label=await classify_candidate_dialogue_chain.ainvoke({'bot_dialogue': bot_dialogue,'candidate_dialogue': candidate_dialogue, 'chat_history': chat_history,'distilled_candidate_dialogue': distilled_candidate_dialogue })
    return candidate_dialogue_label    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9095)