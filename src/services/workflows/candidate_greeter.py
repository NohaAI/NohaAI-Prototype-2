from src.dao.user import get_user_metadata
from src.utils.logger import get_logger

logger=get_logger(__name__)

async def generate_greeting(user_id: int):
    username= await get_user_metadata(user_id)
    greeting= f"Hello {username['name']}, I am Noha. I'm your interviewer today. We have planned a data structures and algorithms interview with you, are you good to go?" # put this MESSAGE in the config/constants file ??
    return greeting
