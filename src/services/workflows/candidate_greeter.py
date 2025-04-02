from src.dao.user import get_user_metadata
from src.config import constants as CONST
from src.utils import logger as LOGGER

async def generate_greeting(user_id: int):
    LOGGER.log_info("\n>>>>>>>>>>>FUNCTION [generate_greeting] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    username= await get_user_metadata(user_id)
    print(username['name'])
    greeting= f"Hello {username['name']}, {CONST.GREETING_SUFFIX}"
    LOGGER.log_info("\n>>>>>>>>>>>FUNCTION EXIT [generate_greeting] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    return greeting