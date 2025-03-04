from fastapi import FastAPI
import uvicorn
from src.utils import logger
from src.services.llm import llm_service
from src.services.llm.prompts.policy_violation_prompt import policy_violation_prompt_template
logger = logger.get_logger(__name__)
app=FastAPI()

@app.get('/policy_violation_service')
async def check_policy_violation(question ,answer , interim_chat_history,hint=None):
    if not hint:
        follow_up_question=""
    follow_up_question=hint
    policy_violation_prompt=policy_violation_prompt_template()
    llm_model = llm_service.get_openai_model()
    policy_violation_chain=(policy_violation_prompt|llm_model)
    check_policy_violation=await policy_violation_chain.ainvoke({'question': question, 'follow_up_question': follow_up_question, 'answer': answer,'interim_chat_history' : interim_chat_history})
    return check_policy_violation

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)