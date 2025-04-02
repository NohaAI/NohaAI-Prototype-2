from typing import Any
from src.config import logging_config as LOGCONF
from src.config import constants as CONST
import importlib.resources as res
from fastapi.responses import JSONResponse
from fastapi import status
import json
import os
from datetime import datetime



def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def decorate_response(succeeded: bool, message: Any, status_code: int = status.HTTP_200_OK) -> JSONResponse:
    """Creates a standardized JSON response.

    Args:
        succeeded: Whether the operation succeeded.
        message: The response message or data.
        status_code: HTTP status code for the response.

    Returns:
        JSONResponse: Formatted response with consistent structure.
    """
    return JSONResponse(
        content={
            "succeeded": succeeded,
            "message": message,
            "httpStatusCode": status_code
        },
        status_code=status_code
    )

def filter_chat_history(chat_history, question_id):
    filtered_chat_history = []
    for entry in chat_history:
        if entry.get("question_id") == question_id:
            filtered_chat_history.append({
                "bot_dialogue": entry.get("bot_dialogue"),
                "candidate_dialogue": entry.get("distilled_candidate_dialogue")
            })
    return filtered_chat_history


def calculate_overall_score(assessment_payloads):
    overall_score = 0
    for assessment_payload in assessment_payloads:
        overall_score += assessment_payload['assessment_payloads'][-1]['final_score']
        total_possible_score = len(assessment_payloads) * 10
    return overall_score, total_possible_score

def convert_assessment_payload_object_to_dict(assessment_payloads):
    
    assessment_payload_dict_list = []
    
    for record in assessment_payloads:
        assessment_payload_dict = {
            'interview_id': record.interview_id,
            'question_id': record.question_id,
            'primary_question_score': record.primary_question_score,
            'assessment_payloads': record.assessment_payload,
            }
        assessment_payload_dict_list.append(assessment_payload_dict)
    
    return assessment_payload_dict_list

def convert_chat_history_object_to_dict(chat_history_records):
    chat_history_dicts = []
    for record in chat_history_records:
        chat_dict = {
            'interview_id': record.interview_id,
            'question_id': record.question_id,
            'bot_dialogue_type': record.bot_dialogue_type,
            'bot_dialogue': record.bot_dialogue,
            'candidate_dialogue': record.candidate_dialogue,
            'distilled_candidate_dialogue': record.distilled_candidate_dialogue
        }
        chat_history_dicts.append(chat_dict)
    return chat_history_dicts

def write_to_pdf(buffer, file_path):
    if file_path:
        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())

def clean_response(response):
    cleaned_subcriteria = (response.replace("```python", "").replace("```'", "").replace("\n", "").replace("'", "").replace("```", "").replace("json", ""))
    return cleaned_subcriteria

def get_assessment_payload():
    """
    Loads a fresh instance of the assessment_payload from the JSON schema file.

    Returns:
        dict: The loaded assessment payload.
    """
    try:
        return json.load(res.open_text(CONST.ASSESSMENT_PAYLOAD_SCHEMA_PATH, CONST.ASSESSMENT_PAYLOAD_SCHEMA)) # todo: the path of this json file has to be added to configuration constants
    except Exception as e:
        raise RuntimeError(f"Error loading assessment_payload.json: {e}")


def transform_subcriteria(input_data):
    # Initialize a dictionary to store the transformed data
    result = {}

    for item in input_data:
        main_criteria = str(item[2])  # Extract the main criteria as a string
        subcriterion = item[1]       # Extract the subcriterion
        weight = str(item[4])        # Extract the weight as a string

        # If the main criteria doesn't exist in the result, initialize it
        if main_criteria not in result:
            result[main_criteria] = {
                'subcriteria': [],
                'weight': []
            }

        # Append the subcriterion and weight to the respective lists
        result[main_criteria]['subcriteria'].append(subcriterion)
        result[main_criteria]['weight'].append(weight)

    return result
        
def filter_by_key(data, key, value):
    return [item for item in data if item.get(key) == value]

def get_subcriteria_scores(assessment_payload):
    """
    Extracts subcriteria scores from the assessment payload.

    Args:
        assessment_payload (dict): The assessment payload.

    Returns:
        list: A list of subcriteria scores.
    """
    return [criterion.get("subcriteria_scores", []) for criterion in assessment_payload.get("criteria", [])]

def get_criteria_scores(assessment_payload):
    """
    Extracts criteria scores from the assessment payload.

    Args:
        assessment_payload (dict): The assessment payload.

    Returns:
        list: A list of criteria scores.
    """
    return [criterion.get("criteria_scores", []) for criterion in assessment_payload.get("criteria", [])]