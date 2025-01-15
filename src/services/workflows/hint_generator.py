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
from src.dao.criterion import fetch_criteria
from src.services.llm.prompts.hint_prompt import hint_prompt_template,hint_prompt_template_if_else,hint_prompt_template_assumption_corner_cases,hint_prompt_template_data_structures,hint_prompt_template_algorithms,hint_prompt_template_time_complexity,hint_prompt_template_space_complexity
# Initialize logger
logger = get_logger(__name__)

async def generate_hint(chat_history,answer_evaluation,hint_count):
    criteria=await fetch_criteria(1)
    if isinstance(answer_evaluation, str):
        answer_evaluation = json.loads(answer_evaluation)
    subcriteria_list=[]
    for i in range(0,21):
        subcriterion = list(answer_evaluation["evaluation_results"][i].keys())[0]
        subcriteria_list.append(subcriterion)
    hint_prompt=hint_prompt_template()
    hint_prompt_if_else=hint_prompt_template_if_else()
    hint_prompt_asc=hint_prompt_template_assumption_corner_cases()
    hint_prompt_ds=hint_prompt_template_data_structures()
    hint_prompt_a=hint_prompt_template_algorithms()
    hint_prompt_tc=hint_prompt_template_time_complexity()
    hint_prompt_sc=hint_prompt_template_space_complexity()
    llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")

    logger.info(f"ANSWER EVALUATION {answer_evaluation}")
    logger.info(f"HINT COUNT AFTER {len(chat_history)} : {hint_count}")
    assumption_score = answer_evaluation["criteria_scores"][0]          
    corner_case_score = answer_evaluation["criteria_scores"][1]        
    data_structures_score = answer_evaluation["criteria_scores"][2]
    algorithm_score = answer_evaluation["criteria_scores"][3]   
    time_complexity_score = answer_evaluation["criteria_scores"][4]    
    space_complexity_score = answer_evaluation["criteria_scores"][5]    
    #check for counter 
    if (assumption_score < 0.2 or corner_case_score < 0.2) and hint_count[0] < 2:
        hint_count[0] += 1

        criteria_list=[]
        criteria_list.append(criteria[1])
        criteria_list.append(criteria[2])
        hint_chain_asc=(hint_prompt_asc|llm_model)
        #hint=await hint_chain_if_else.ainvoke({'chat_history':chat_history,'criteria': criteria_list, 'subcriteria':subcriteria_list[0:6]})
        hint=await hint_chain_asc.ainvoke({'chat_history':chat_history, 'subcriteria':subcriteria_list[0:6]})
        return hint.content

    if data_structures_score < 0.4 and hint_count[1] < 2:
        hint_count[1] += 1
        
        hint_chain_ds=(hint_prompt_ds|llm_model)
        hint=await hint_chain_ds.ainvoke({'chat_history':chat_history, 'subcriteria':subcriteria_list[6:9]})
        #hint=await hint_chain_if_else.ainvoke({'chat_history':chat_history,'criteria': criteria_list, 'subcriteria':subcriteria_list[6:9]})
        
        return hint.content

    if algorithm_score < 0.4 and hint_count[2] < 2:
        hint_count[2] += 1

        criteria_list=[]
        criteria_list.append(criteria[4])

        hint_chain_a=(hint_prompt_a|llm_model)
        hint=await hint_chain_a.ainvoke({'chat_history':chat_history,'criteria': criteria_list, 'subcriteria':subcriteria_list[9:12]})
        
        return hint.content

    if time_complexity_score < 0.4 and hint_count[3] < 2:
        hint_count[3] += 1

        criteria_list=[]
        criteria_list.append(criteria[5])
        
        hint_chain_tc=(hint_prompt_tc|llm_model)
        hint=await hint_chain_tc.ainvoke({'chat_history':chat_history,'criteria': criteria_list, 'subcriteria':subcriteria_list[13:16]})
        
        return hint.content

    if space_complexity_score < 0.4 and hint_count[4] < 2:
        hint_count[4] += 1

        criteria_list=[]
        criteria_list.append(criteria[6])
        
        hint_chain_sc=(hint_prompt_sc|llm_model)
        hint=await hint_chain_sc.ainvoke({'chat_history':chat_history,'criteria': criteria_list, 'subcriteria':subcriteria_list[15:18]})
    
        return hint.content
        

    hint_chain=(hint_prompt|llm_model)
    hint=await hint_chain.ainvoke({'chat_history':chat_history,'answer_evaluation':answer_evaluation})
    return hint.content
