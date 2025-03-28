from typing import Any
import logging
from src.utils.logger import get_logger
from src.config import constants as CONST
import importlib.resources as res
from fastapi.responses import JSONResponse
from fastapi import status
import json
import os
from datetime import datetime


 # Configure logger if not already set up
logger = get_logger(__name__)

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

def pretty_log_temp(title: str, data, log_level=logging.INFO):
    """
    Logs a structured dictionary or list in a pretty JSON format.

    Args:
        title (str): A descriptive title for the log entry.
        data (dict | list | any): The structured data to log.
        log_level (int, optional): Logging level (default is logging.INFO).
    """

    try:
        if isinstance(data, list): 
            if str(data) == "assessment":
                print("INSIDE HELPER IF")
                primary_question_score = str(data[-1]['primary_question_score'])
                logger.log(log_level, primary_question_score)
                criteria_scores = str(data[-1]['criteria_scores'])
                logger.log(log_level, criteria_scores)
                subcriteria_scores = str(data[-1]['subcriteria_scores'])
                logger.log(log_level, subcriteria_scores)
            else:
                pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
        elif isinstance(data, dict):
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
        else:
            pretty_data = str(data)

        log_message = f"\n==== {title} ====\n{pretty_data}\n================="
        logger.log(log_level, log_message)
    except Exception as e:
        logger.error(f"Error while logging {title}: {e}")
        

def pretty_log_for_local(title: str, data, log_level=0):
    """
    Logs a structured dictionary or list in a pretty JSON format.

    Args:
        title (str): A descriptive title for the log entry.
        data (dict | list | any): The structured data to log.
        log_level (int, optional): Logging level (default is logging.INFO).
    """
    try:
        if isinstance(data, (dict, list)):  
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
        else:
            pretty_data = str(data)

        log_message = f"\n==== {title} ====\n{pretty_data}\n================="

        # Handle integer logging levels properly
        if isinstance(log_level, int) and log_level not in [
            logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        ]:
            if log_level == 1:
                # print(f"[LOG LEVEL {log_level}] {log_message}")
                print(f"{log_message}")
        else:
            logger.log(log_level, log_message)
    except Exception as e:
        logger.error(f"Error while logging {title}: {e}")

        # Assuming logger is already configured elsewhere to write to FILElog
def pretty_log(title: str, data, log_level=1):
    """
    Logs a structured dictionary or list in a pretty JSON format.
    Prints to console and appends to FILElog.

    Args:
        title (str): A descriptive title for the log entry.
        data (dict | list | any): The structured data to log.
        log_level (int, optional): Logging level (default is logging.INFO).
    """
    try:
        # Convert data to pretty JSON if it's a dict or list
        if isinstance(data, (dict, list)):  
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
        else:
            pretty_data = str(data)

        log_message = f"\n==== {title} ====\n{pretty_data}\n================="

        # Always print to console
        print(log_message)

        # Log to FILElog using the logger
        if isinstance(log_level, int) and log_level not in [
            logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        ]:
            if log_level == 1:
                logger.info(log_message)  # Default to INFO if an invalid level is given
        else:
            logger.log(log_level, log_message)  # Log at specified level
    except Exception as e:
        logger.error(f"Error while logging {title}: {e}")

def pretty_log_list(title: str, data, log_level=0):
    """
    Logs a structured dictionary or list in a pretty JSON format.

    Args:
        title (str): A descriptive title for the log entry.
        data (dict | list | any): The structured data to log.
        log_level (int, optional): Logging level (default is logging.INFO).
    """
    try:
        if isinstance(data, (dict)):  
            pretty_data = json.dumps(data, indent=4, ensure_ascii=False)
        else:
            pretty_data = str(data)

        log_message = f"\n==== {title} ====\n{pretty_data}\n================="
        logger.log(log_level, log_message)
    except Exception as e:
        logger.error(f"Error while logging {title}: {e}")

def filter_by_key(data, key, value):
    return [item for item in data if item.get(key) == value]