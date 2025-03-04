from src.dao.user import get_user_metadata
from src.utils.logger import get_logger

logger=get_logger(__name__)

async def generate_greeting(user_id: int):
    username= await get_user_metadata(user_id)
    greeting= f"Hi {username['name']} hope you are doing well! Shall we begin the interview?"
    return greeting
