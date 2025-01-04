from src.dao.question import get_question_metadata
from src.dao.interview import get_interview_metadata
from src.dao.user import get_user_metadata
from src.utils.logger import get_logger

logger=get_logger(__name__)

async def generate_greeting(user_id: int, question_id: int):
    username= await get_user_metadata(user_id)
    question_metadata= await get_question_metadata(question_id)
    greeting= f"Hi {username['name']} hope you are doing well! Shall we begin the interview?"
    #response ="Yeah sure I can get started"
    # greeting=f"Hi {username['name']} I want you to answer the following {question_metadata['question_type']} for me : {question_metadata['question']}"
    return greeting
