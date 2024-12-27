from pydantic import BaseModel,Field

class UserResponse(BaseModel):
    """
    Pydantic model for user response structure.
    
    Attributes:
        user_id (int): Unique identifier for the user
        name (str): User's name, must be between 2 and 50 characters
    """
    user_id: int
    name: str = Field(..., min_length=2, max_length=50)

class UserRequest(BaseModel):
    """
    Pydantic model for user creation/update requests.
    
    Attributes:
        name (str): User's name, must be between 2 and 50 characters
    """
    name: str = Field(..., min_length=2, max_length=50)
