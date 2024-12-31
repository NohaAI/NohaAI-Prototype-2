from fastapi import FastAPI , Depends
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
from src.dao.utils.DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.Exceptions import RoleProfileCriterionWeightNotFoundException
from src.schemas.dao.schema import RoleProfileCriterionWeightRequest,RoleProfileCriterionWeightResponse

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/role_profile/{role_profile_id}", response_model=RoleProfileCriterionWeightResponse)
async def get_role_profile_criterion_weight_metadata(role_profile_id: int):
    """
    Retrieve role_profile_criterion_weight information by ID.
    
    Args:
        role_profile_id (int): ID of the organization to retrieve
        
    Returns:
        RoleProfileCriterionWeightResponse: role_profile_criterion_weight details
        
    Raises:
        Exception: 404 if role_profile not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            get_role_profile_criterion_weight_query="SELECT role_profile_id, criterion_weight_json FROM role_profile_criterion_weight WHERE role_profile_id = %s"
            role_profile_criterion_weight_metadata = execute_query(conn,get_role_profile_criterion_weight_query,(role_profile_id,))
            if not role_profile_criterion_weight_metadata:
                raise OrganizationNotFoundException(role_profile_id)
            return {"role_profile_id": role_profile_criterion_weight_metadata[0], "criterion_weight_json": role_profile_criterion_weight_metadata[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e


@app.post("/role_profile-service", response_model=RoleProfileCriterionWeightResponse)
async def add_role_profile_criterion_weight(role_profile_id:int, criterion_weight_json: str):
    """
    Create a new organization.
    
    Args:
        organization (str): Name of the organization to create
        
    Returns:
        RoleProfileCriterionWeightResponse: Created role_profile_criterion_weight details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:
            cur_query = "INSERT INTO role_profile_criterion_weight (role_profile_id,criterion_weight_json) VALUES ( %s, %s) RETURNING role_profile_id, criterion_weight_json"
            role_profile_criterion_weight = execute_query(conn,cur_query,(role_profile_id,criterion_weight_json,),commit=True)
            return {"role_profile_id": role_profile_criterion_weight[0], "criterion_weight_json": role_profile_criterion_weight[1]}    
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/role_profile-service/{role_profile_id}", response_model=RoleProfileCriterionWeightResponse)
async def update_role_profile_criterion_weight(role_profile_id: int, role_profile_criterion_weight_request: RoleProfileCriterionWeightRequest):
    """
    Update an existing organization's information.
    
    Args:
        role_profile_id (int): ID of the organization to update
        organization (RoleProfileCriterionWeightRequest): Updated organization information
        
    Returns:
        RoleProfileCriterionWeightResponse: Updated organization details
        
    Raises:
        Exception: 404 if organization not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = "UPDATE role_profile_criterion_weight SET criterion_weight_json = %s WHERE role_profile_id = %s RETURNING role_profile_id, criterion_weight_json"
            updated_role_profile_criterion_weight = execute_query(conn,update_query,(role_profile_criterion_weight_request.criterion_weight_json, role_profile_id),commit=True)
            if not updated_role_profile_criterion_weight:
                raise OrganizationNotFoundException(role_profile_id)         
            return {"role_profile_id": updated_role_profile_criterion_weight[0], "criterion_weight_json": updated_role_profile_criterion_weight[1]} 
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/role_profile-service/{role_profile_id}", response_model=dict)
async def delete_role_profile_criterion_weight(role_profile_id: int):
    """
    Delete a organization by ID.
    
    Args:
        role_profile_id (int): ID of the organization to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if organization not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM role_profile_criterion_weight WHERE role_profile_id = %s RETURNING role_profile_id"
            deleted_role_profile_criterion_weight = execute_query(
                conn,
                delete_query,
                (role_profile_id,),
                commit=True
            )
            
            if not deleted_role_profile_criterion_weight:
                raise OrganizationNotFoundException(role_profile_id)
            
            return {"message": "organization deleted successfully"}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9093)
