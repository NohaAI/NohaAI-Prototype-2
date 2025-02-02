from fastapi import FastAPI
import uvicorn
from src.utils import logger
from src.services.llm import llm_service
from src.services.llm.prompts.policy_violation_prompt import guardrails_check_prompt_template
logger = logger.get_logger(__name__)
app=FastAPI()

@app.get('/guardrails_check')
async def guardrails_check(question ,answer):

    guardrails_check_prompt=guardrails_check_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    guardrails_check_chain=(guardrails_check_prompt|llm_model)
    guardrails_check=await guardrails_check_chain.ainvoke({'question': question,'answer': answer})
    return guardrails_check

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9095)