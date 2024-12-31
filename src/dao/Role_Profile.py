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
from src.dao.Exceptions import RoleProfileNotFoundException,OrganizationNotFoundException
from src.schemas.dao.schema import RoleProfileResponse,RoleProfileRequest

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/role_profile/{role_profile_id}", response_model=RoleProfileResponse)
async def get_role_profile_metadata(role_profile_id: int):
    """
    Retrieve role_profile information by ID.
    
    Args:
        role_profile_id (int): ID of the role_profile to retrieve
        
    Returns:
        RoleProfileResponse: Role profile details
        
    Raises:
        Exception: 404 if role_profile not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            get_role_profile_query="SELECT role_profile_id, role_profile,level,organization_id FROM role_profile WHERE role_profile_id = %s"
            role_profile_metadata = execute_query(conn,get_role_profile_query,(role_profile_id,))
            if not role_profile_metadata:
                raise RoleProfileNotFoundException(role_profile_id)
            return {"role_profile_id": role_profile_metadata[0], "role_profile": role_profile_metadata[1],'level':role_profile_metadata[2],'organization_id':role_profile_metadata[3]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e


@app.post("/role_profile", response_model=RoleProfileResponse)
async def add_role_profile(role_profile: str, organization_id: int, level: str):
    """
    Create a new role_profile.
    
    Args:
        role_profile (str): Name of the role_profile to create
        
    Returns:
        RoleProfileResponse: Created role_profile details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:
            organization_check_query="SELECT organization FROM organization WHERE organization_id=%s"
            organization=execute_query(conn,organization_check_query,(organization_id,))
            if not organization:
                raise OrganizationNotFoundException
            role_profile_insert_query = "INSERT INTO role_profile (role_profile,level,organization_id) VALUES ( %s, %s, %s) RETURNING role_profile_id, role_profile,level,organization_id"
            role_profile = execute_query(conn,role_profile_insert_query,(role_profile,level,organization_id),commit=True)
            return {"role_profile_id": role_profile[0], "role_profile": role_profile[1],'level':role_profile[2],'organization_id':role_profile[3]}    
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/role_profile/{role_profile_id}", response_model=RoleProfileResponse)
async def update_role_profile(role_profile_id: int, role_profile: RoleProfileRequest):
    """
    Update an existing role_profile's information.
    
    Args:
        role_profile_id (int): ID of the role_profile to update
        role_profile (RoleProfileRequest): Updated role_profile information
        
    Returns:
        RoleProfileResponse: Updated role_profile details
        
    Raises:
        Exception: 404 if role_profile not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = "UPDATE role_profile SET role_profile = %s,level=%s WHERE role_profile_id = %s RETURNING role_profile_id, role_profile, level, organization_id"
            updated_role_profile = execute_query(conn,update_query,(role_profile.role_profile, role_profile.level,role_profile_id),commit=True)
            if not updated_role_profile:
                raise RoleProfileNotFoundException(role_profile_id)         
            return {"role_profile_id": updated_role_profile[0], "role_profile": updated_role_profile[1],"level":updated_role_profile[2],"organization_id":updated_role_profile[3]} 
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/role_profile/{role_profile_id}", response_model=dict)
async def delete_role_profile(role_profile_id: int):
    """
    Delete a role_profile by ID.
    
    Args:
        role_profile_id (int): ID of the role_profile to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if role_profile not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM role_profile WHERE role_profile_id = %s RETURNING role_profile_id"
            deleted_role_profile = execute_query(
                conn,
                delete_query,
                (role_profile_id,),
                commit=True
            )
            
            if not deleted_role_profile:
                raise RoleProfileNotFoundException(role_profile_id)
            
            return {"message": "role profile deleted successfully"}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9093)
