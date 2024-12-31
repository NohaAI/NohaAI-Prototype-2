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

class OrganizationResponse(BaseModel):
    """
    Pydantic model for organization response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    organization_id: int  # Corrected the typo here
    organization: str = Field(..., min_length=2, max_length=50)


class OrganizationRequest(BaseModel):
    """
    Pydantic model for user creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    organization: str = Field(..., min_length=2, max_length=50)

class RoleProfileResponse(BaseModel):
    """
    Pydantic model for role profile response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile_id: int  # Corrected the typo here
    role_profile: str = Field(..., min_length=2, max_length=50)
    level:str = Field(...,max_length=20)
    organization_id: int

class RoleProfileRequest(BaseModel):
    """
    Pydantic model for role profile creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile: str = Field(..., min_length=2, max_length=50)
    level:str = Field(...,max_length=20)

class RoleProfileCriterionWeightResponse(BaseModel):
    """
    Pydantic model for role profile criterion weight response structure.
    
    Attributes:
        organization_id (int): Unique identifier for the user
        organization (str): organization's name, must be between 2 and 50 characters
    """
    role_profile_id: int  
    criterion_weight_json: str

class RoleProfileCriterionWeightRequest(BaseModel):
    """
    Pydantic model for role profile criterion weight creation/update requests.
    
    Attributes:
        organization (str): organization's name, must be between 2 and 50 characters
    """
    criterion_weight_json: str
