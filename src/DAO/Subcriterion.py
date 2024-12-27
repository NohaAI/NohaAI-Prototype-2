from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Optional, Union
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import uvicorn
from src.dao.utils.DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.Exceptions import QuestionNotFoundException,SubcriterionNotFoundException
from src.dao.CriterionPayload import Criterion,SubCriterion
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Pydantic Models with Documentation
class SubcriteriaResponse(BaseModel):
    """
    Response model for subcriterion data.
    Attributes:
        subcriterion_id (int): Unique identifier for the subcriterion
        subcriteria (str): Name of the subcriterion, between 2 and 100 characters
        criterion_id (int): ID of the parent category
        question_id (int): ID of the associated question
    """
    subcriterion_id: int
    subcriteria: str = Field(..., min_length=2, max_length=100)
    criterion_id: int
    question_id: int
class SubcriteriaRequest(BaseModel):
    """
    Request model for creating/updating subcriteria.
    Attributes:
        subcriteria (str): Name of the subcriterion, between 2 and 100 characters
        criterion_id (Optional[int]): Optional ID of the parent category
        question_id (int): ID of the associated question
    """
    subcriteria: str = Field(..., min_length=2, max_length=100)
    criterion_id: Optional[int] = None
    question_id: int
class SubcriteriaUpdate(BaseModel):
    """
    Model for updating existing subcriteria.
    Attributes:
        subcriteria (str): New name for the subcriterion, between 2 and 100 characters
    """
    subcriteria: str = Field(..., min_length=2, max_length=100)
class ParsedMetrics(BaseModel):
    """
    Model for batch inserting metrics data.
    Attributes:
        question_id (int): ID of the question these metrics belong to
        input_data (Dict[str, Dict[str, List[str]]]): Nested dictionary containing criteria,
            their submetrics, and corresponding weights
    """
    question_id: int
    input_data: Dict[str, Dict[str, List[str]]]
app = FastAPI()

@app.get("/subcriteria/{subcriterion_id}", response_model=SubcriteriaResponse)
async def get_subcriterion(subcriterion_id: int):
    """
    Retrieve a subcriterion by ID.
    Args:
        subcriterion_id (int): ID of the subcriterion to retrieve
    Returns:
        SubcriteriaResponse: subcriterion details
    Raises:
        HTTPException: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            query = """
                SELECT subcriterion_id, subcriteria, criterion_id, question_id
                FROM Subcriterion
                WHERE subcriterion_id = %s
            """
            category = execute_query(conn, query, (subcriterion_id,))
            if not category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {
                "subcriterion_id": category[0],
                "subcriteria": category[1],
                "criterion_id": category[2],
                "question_id": category[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/subcriteria")
async def fetch_subcriteria(question_id: int):
    try:
        with get_db_connection() as conn:
            query = """
                SELECT 
                    Criterion.criterion,
                    Subcriterion.subcriterion,
                    Subcriterion.weight
                FROM Subcriterion
                JOIN Criterion ON Criterion.criterion_id = Subcriterion.criterion_id
                WHERE Subcriterion.question_id = %s
            """
            
            results = execute_query(conn, query, (question_id,), fetch_one=False)
            
            if not results:
                return {}

            criteria_dict = {}
            
            for criterion_name, subcriterion_name, weight in results:
                if criterion_name not in criteria_dict:
                    criteria_dict[criterion_name] = Criterion(criterion_name)
                
                subcriterion = SubCriterion(subcriterion_name, float(weight))
                criteria_dict[criterion_name].add_subcriterion(subcriterion)

            return {
                name: [{"subcriterion": sub.name, "weight": sub.weight} 
                      for sub in criterion.subcriteria]
                for name, criterion in criteria_dict.items()
            }

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
@app.post("/subcriteria/batch_insert", response_model=List)
async def batch_insert_subcriteria(
    question_id: int,
    subcriteria_data: Dict[str, Dict[str, Union[List[str], List[int]]]]
    ) -> tuple[bool, str]:
    """
    Batch insert subcriteria into the database with question_id.
    Args:
        question_id (int): The ID of the question associated with the subcriteria.
        subcriteria_data (dict): Input data containing subcriteria and weights keyed by criterion_id.
            Format: {
                "criterion_id": {
                    "subcriteria": ["subcriterion1", "subcriterion2", ...],
                    "weight": [weight1, weight2, ...]
                }
            }
    Returns:
        tuple[bool, str]: (Success status, Message describing the result)
    """
    # Input validation
    if not isinstance(question_id, int) or question_id <= 0:
        return False, "Invalid question_id"
    # Validate subcriteria data structure
    for criterion_id, data in subcriteria_data.items():
        if not all(key in data for key in ["subcriteria", "weight"]):
            return False, f"Missing required keys for criterion_id {criterion_id}"
        if len(data["subcriteria"]) != len(data["weight"]):
            return False, f"Mismatched subcriteria and weight lengths for criterion_id {criterion_id}"
    query = """
        INSERT INTO Subcriterion (subcriterion, criterion_id, question_id, weight)
        VALUES (%s, %s, %s, %s)
    """

    with get_db_connection() as connection:
        for criterion_id, criterion_data in subcriteria_data.items():
            subcriteria = criterion_data["subcriteria"]
            weights = criterion_data["weight"]
            for subcriterion, weight in zip(subcriteria, weights):
                params = (
                    subcriterion,
                    int(criterion_id),
                    question_id,
                    weight
                )
                execute_query(
                    connection=connection,
                    query=query,
                    params=params,
                    fetch_one=False,
                    commit=False
                )
        # Final commit after all inserts
        connection.commit()
    return True, "Successfully inserted subcriteria"
        

# async def batch_insert_subcriteria(input_payload: ParsedMetrics):
#     """
#     Batch insert subcriteria.
#     Args:
#         input (ParsedMetrics): Object containing question_id and input_data with
#             criteria, submetrics, and weights
#     Returns:
#         List: The inserted subcriteria
#     Raises:
#         HTTPException: 400 for validation errors, 503 for connection issues,
#                       500 for other database errors
#     """
#     try:
#         with get_db_connection() as conn:
#             subcriteria = []
#             for criterion_id, data in input_payload.input_data.items():
#                 if len(data['subcriteria']) != len(data['weight']):
#                     raise HTTPException(
#                         status_code=400,
#                         detail=f"Mismatch in number of subcriteria and weights for category {criterion_id}"
#                     )
#                 subcriteria.extend([
#                     (int(criterion_id), str(subcriteria), input_payload.question_id, int(weight))
#                     for subcriteria, weight in zip(data['subcriteria'], data['weight'])
#                 ])
#             cursor = conn.cursor()
#             try:
#                 insert_query = """
#                     INSERT INTO Subcriteria
#                         (criterion_id, subcriterion, question_id, weight)
#                     VALUES %s
#                     RETURNING subcriterion_id, criterion_id, subcriterion,
#                         question_id, weight
#                 """
#                 execute_values(cursor, insert_query, subcriteria)
#                 conn.commit()
#                 return subcriteria
#             finally:
#                 cursor.close()
#     except DatabaseConnectionError as e:
#         raise e
#     except DatabaseQueryError as e:
#         raise e
#     except DatabaseOperationError as e:
        # raise e
@app.put("/subcriteria/{subcriterion_id}", response_model=SubcriteriaResponse)
async def update_subcriterion(subcriterion_id: int, update_data: SubcriteriaUpdate):
    """
    Update an existing subcriterion.
    Args:
        subcriterion_id (int): ID of the subcriterion to update
        update_data (SubcriteriaUpdate): New data for the subcriterion
    Returns:
        SubcriteriaResponse: Updated subcriterion details
    Raises:
        HTTPException: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = """
                UPDATE Subcriterion
                SET subcriterion = %s
                WHERE subcriterion_id = %s
                RETURNING subcriterion_id, subcriterion, criterion_id, question_id
            """
            updated_category = execute_query(
                conn,
                update_query,
                (update_data.subcriteria, subcriterion_id),
                commit=True
            )
            if not updated_category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {
                "subcriterion_id": updated_category[0],
                "subcriteria": updated_category[1],
                "criterion_id": updated_category[2],
                "question_id": updated_category[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
@app.delete("/subcriteria/{subcriterion_id}", response_model=dict)
async def delete_subcriterion(subcriterion_id: int):
    """
    Delete a subcriterion by ID.
    Args:
        subcriterion_id (int): ID of the subcriterion to delete
    Returns:
        dict: Success message
    Raises:
        HTTPException: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = """
                DELETE FROM Subcriterion
                WHERE subcriterion_id = %s
                RETURNING subcriterion_id
            """
            deleted_category = execute_query(
                conn,
                delete_query,
                (subcriterion_id,),
                commit=True
            )
            if not deleted_category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {"message": "subcriterion deleted successfully"}
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9092)