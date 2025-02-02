from fastapi import FastAPI
import uvicorn
from src.utils import logger
from src.services.llm import llm_service
from src.services.llm.prompts.answer_classifier_prompt import classify_candidate_answer_prompt_template
logger = logger.get_logger(__name__)

app=FastAPI()

@app.get('/classify_candidate_answer')
async def classify_candidate_answer(question, candidate_answer, chat_history, follow_up_question=None):
    classify_candidate_answer_prompt=classify_candidate_answer_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    classify_candidate_answer_chain=(classify_candidate_answer_prompt|llm_model)
    candidate_answer_label=await classify_candidate_answer_chain.ainvoke({'question': question, 'follow_up_question': follow_up_question,'answer': candidate_answer, 'chat_history': chat_history })
    return candidate_answer_label    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9095)