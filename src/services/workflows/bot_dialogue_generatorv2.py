from fastapi import FastAPI
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
from src.dao.criterion import fetch_criteria
from src.services.llm.prompts.bot_dialogue_prompt import bot_dialogue_prompt_template 
from src.services.llm.prompts.hint_prompt import hint_prompt_template,hint_prompt_template_if_else,hint_prompt_template_assumption_corner_cases,hint_prompt_template_data_structures,hint_prompt_template_algorithms,hint_prompt_template_time_complexity,hint_prompt_template_space_complexity
# Initialize logger
logger = get_logger(__name__)

async def generate_dialogue(label, chat_history, answer, question, hint_count, answer_evaluation=None, previous_dialogue=None,rationale=None):
    # non_technical_class_labels=["illegible", "irrelevant", "clarification(specific)", "clarification(open)", "request(guidance)", "request(termination)", "request(proceed)", "request(break)", "disregard", "illegitimate", "uncertainty"]
    if not previous_dialogue:
        follow_up_question=""
    if not rationale:
        rationale=""
    if not answer_evaluation:
        answer_evaluation={}
    
    follow_up_question=previous_dialogue
    bot_dialogue_prompt=bot_dialogue_prompt_template()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
    bot_dialogue_prompt_chain=(bot_dialogue_prompt|llm_model)
    bot_dialogue=await bot_dialogue_prompt_chain.ainvoke({'class': label, 'question': question, 'follow_up_question': follow_up_question, 'answer': answer,'chat_history' : chat_history, 'rationale': rationale, 'answer_evaluation' : answer_evaluation})
    return bot_dialogue