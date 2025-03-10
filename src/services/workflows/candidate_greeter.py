from src.dao.user import get_user_metadata
from src.utils.logger import get_logger
from src.config import constants as CONST

logger=get_logger(__name__)

async def generate_greeting(user_id: int):
    username= await get_user_metadata(user_id)
    print(username['name'])
    greeting= f"Hello {username['name']}, {CONST.GREETING_SUFFIX}"
    return greeting
