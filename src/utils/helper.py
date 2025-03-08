from typing import Any
from src.utils.logger import get_logger
from fastapi.responses import JSONResponse
from fastapi import status
import json
import os

 # Configure logger if not already set up
logger = get_logger(__name__)

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


def clean_response(response):
    cleaned_subcriteria = (response.replace("```python", "").replace("```'", "").replace("\n", "").replace("'", "").replace("```", "").replace("json", ""))
    return cleaned_subcriteria

def get_assessment_payload():
    file_path = os.path.join("src", "schemas", "evaluation", "assessment_payload.json")
    with open(file_path, "r") as file:
        assessment_payload = json.load(file)  
    return assessment_payload


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

def pretty_log(title: str, data, log_level=logging.INFO):
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
        logger.log(log_level, log_message)
    except Exception as e:
        logger.error(f"Error while logging {title}: {e}")