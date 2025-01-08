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

async def generate_hint(chat_history,answer_evaluation,hint_count):
    
    if isinstance(answer_evaluation, str):
        answer_evaluation = json.loads(answer_evaluation)
    
    hint_questions = {
        "assumption_corner_case_hint_question": "Can you elaborate on the scope by clarifying on the assumptions and corner cases further?",
        "data_structures_hint_question": "Can you rethink the choice of data structure so that it is optimized for complexity?",
        "algorithm_hint_question": "Can you rethink the choice of algorithm so that it is optimized for complexity?",
        "time_complexity_hint_question": "Can you rethink the choice of time complexity so that it is optimized for complexity?",
        "space_complexity_hint_question": "Can you rethink the choice of space complexity so that it is optimized for complexity?"
    }
    hint_questions_plus = {
    "assumption_corner_case_hint_question": "In your previous solution, assumptions and corner cases were not clearly addressed. Could you rethink and elaborate on these aspects?",
    "data_structures_hint_question": "From your previous approach, the choice of data structure might not be optimal. Could you reconsider it for better efficiency?",
    "algorithm_hint_question": "Based on your previous solution, the algorithm used could be improved for better complexity. Could you rethink your approach?",
    "time_complexity_hint_question": "Your previous solution did not fully optimize time complexity. Could you reassess your approach to achieve better performance?",
    "space_complexity_hint_question": "In your earlier solution, space complexity wasn’t fully optimized. Could you re-evaluate and refine your approach?"
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
    
    #check for counter 
    if (assumption_score < 0.2 or corner_case_score < 0.2) and hint_count[0] < 2:
        if hint_count[0]==1:
            return hint_questions_plus['assumption_corner_case_hint_question']
        hint_count[0] += 1
        return hint_questions['assumption_corner_case_hint_question']

    if data_structures_score < 0.4 and hint_count[1] < 2:
        if hint_count[1]==1:
            return hint_questions_plus['data_structures_hint_question']
        hint_count[1] += 1
        return hint_questions['data_structures_hint_question']

    if algorithm_score < 0.4 and hint_count[2] < 2:
        if hint_count[2]==1:
            return hint_questions_plus['algorithm_hint_question']
        hint_count[2] += 1
        return hint_questions['algorithm_hint_question']

    if time_complexity_score < 0.4 and hint_count[3] < 2:
        if hint_count[3]==1:
            return hint_questions_plus['time_complexity_hint_question']
        hint_count[3] += 1
        return hint_questions['time_complexity_hint_question']

    if space_complexity_score < 0.4 and hint_count[4] < 2:
        if hint_count[4]==1:
            return hint_questions_plus['space_complexity_hint_question']
        hint_count[4] += 1
        return hint_questions['space_complexity_hint_question']
        

    hint_prompt=hint_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    hint_chain=(hint_prompt|llm_model)
    hint=await hint_chain.ainvoke({'chat_history':chat_history,'answer_evaluation':answer_evaluation})
    return hint.content
