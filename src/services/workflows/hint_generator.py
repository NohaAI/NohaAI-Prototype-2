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
import json
from src.services.llm.prompts.hint_prompt import hint_prompt_template
# Initialize logger
logger = get_logger(__name__)

async def generate_hint(chat_history,answer_evaluation):
    
    if isinstance(answer_evaluation, str):
        answer_evaluation = json.loads(answer_evaluation)
    
    hint_questions = {
        "assumption_corner_case_hint_question": "Can you elaborate on the scope by clarifying on the assumptions and corner cases further?",
        "data_structures_hint_question": "Can you rethink the choice of data structure so that it is optimized for complexity?",
        "algorithm_hint_question": "Can you rethink the choice of algorithm so that it is optimized for complexity?",
        "time_complexity_hint_question": "Can you rethink the choice of time complexity so that it is optimized for complexity?",
        "space_complexity_hint_question": "Can you rethink the choice of space complexity so that it is optimized for complexity?"
    }
    
    assumption_score = answer_evaluation["criteria_scores"][0]          
    corner_case_score = answer_evaluation["criteria_scores"][1]        
    data_structures_score = answer_evaluation["criteria_scores"][2]
    algorithm_score = answer_evaluation["criteria_scores"][3]   
    time_complexity_score = answer_evaluation["criteria_scores"][4]    
    space_complexity_score = answer_evaluation["criteria_scores"][5]
    
    # assumption_score = 5         
    # corner_case_score = 5        
    # data_structures_score = 5
    # algorithm_score = 5   
    # time_complexity_score = 5     
    # space_complexity_score = 5

    if assumption_score < 0.2 or corner_case_score < 0.2:
        hint = hint_questions['assumption_corner_case_hint_question']
        return hint
    if data_structures_score < 0.4:
        hint = hint_questions['data_structures_hint_question']
        return hint
    if algorithm_score < 0.4:
        hint = hint_questions['algorithm_hint_question']
        return hint
    if time_complexity_score < 0.4:
        hint = hint_questions['time_complexity_hint_question']
        return hint
    if space_complexity_score < 0.4:
        hint = hint_questions['space_complexity_hint_question']
        return hint
        

    hint_prompt=hint_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    hint_chain=(hint_prompt|llm_model)
    hint=await hint_chain.ainvoke({'chat_history':chat_history,'answer_evaluation':answer_evaluation})
    return hint.content
