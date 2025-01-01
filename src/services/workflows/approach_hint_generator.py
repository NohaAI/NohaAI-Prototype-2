from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Optional, Union
import os
import logging
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.dao.interview import get_interview_metadata
from src.dao.exceptions import InterviewNotFoundException
from src.services.llm import llm_service

from src.services.llm.prompts.approach_hint_prompt import approach_hint_prompt_template
# Initialize logger
logger = get_logger(__name__)

async def approach_hint_generator(interview_id,question,chat_history,answer_evaluation,criterion_weight_json):

    interview_metadata=await get_interview_metadata(interview_id)
    if not interview_metadata:
        raise InterviewNotFoundException
    
    approach_hint_prompt=approach_hint_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    approach_hint_chain=(approach_hint_prompt|llm_model)
    approach_hint=await approach_hint_chain.ainvoke({'question':question,'chat_history':chat_history,'answer_evaluation':answer_evaluation,'criterion_weight_json':criterion_weight_json})
    return approach_hint.content
