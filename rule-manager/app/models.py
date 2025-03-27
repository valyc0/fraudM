from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RuleStatus(str, Enum):
    """Enum for possible rule statuses"""
    CREATED = "created"
    VALIDATING = "validating"
    VALIDATED = "validated"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ERROR = "error"
    INACTIVE = "inactive"

class RuleCreate(BaseModel):
    """Model for creating a new rule"""
    name: Optional[str] = Field(
        None,
        description="Optional name for the rule. If not provided, a name will be generated"
    )
    description: str = Field(
        ...,
        description="Natural language description of the rule",
        min_length=10,
        max_length=2000
    )
    is_active: Optional[bool] = Field(
        False,
        description="Whether the rule should be active upon creation"
    )

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

class RuleUpdate(BaseModel):
    """Model for updating an existing rule"""
    name: Optional[str] = Field(
        None,
        description="New name for the rule"
    )
    description: Optional[str] = Field(
        None,
        description="New natural language description of the rule",
        min_length=10,
        max_length=2000
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether to activate or deactivate the rule"
    )

    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip() if v else v

class Rule(BaseModel):
    """Complete rule model"""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    name: str = Field(..., description="Display name of the rule")
    natural_language: str = Field(..., description="Original natural language description")
    scala_code: str = Field(..., description="Generated Scala code for Flink")
    status: RuleStatus = Field(
        ...,
        description="Current status of the rule"
    )
    created_at: datetime = Field(..., description="Timestamp when the rule was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last update")
    deployed_at: Optional[datetime] = Field(None, description="Timestamp of last deployment")
    version: int = Field(..., description="Version number of the rule")
    is_active: bool = Field(..., description="Whether the rule is currently active")
    
    # Additional metadata
    validation_results: Optional[dict] = Field(
        None,
        description="Results from the last code validation"
    )
    metrics: Optional[dict] = Field(
        None,
        description="Runtime metrics when deployed"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Optional tags for categorizing rules"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

class ValidationResult(BaseModel):
    """Model for code validation results"""
    is_valid: bool = Field(..., description="Whether the code passed validation")
    issues: List[str] = Field(default_factory=list, description="List of validation issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    validated_at: datetime = Field(default_factory=datetime.now, description="When validation was performed")

class RuleDeployment(BaseModel):
    """Model for rule deployment details"""
    rule_id: str = Field(..., description="ID of the deployed rule")
    job_id: Optional[str] = Field(None, description="Flink job ID if deployed")
    deployed_at: Optional[datetime] = Field(None, description="When the rule was deployed")
    status: RuleStatus = Field(..., description="Current deployment status")
    error_message: Optional[str] = Field(None, description="Error message if deployment failed")
    
    # Additional deployment details
    parallelism: Optional[int] = Field(None, description="Flink job parallelism")
    resources: Optional[dict] = Field(None, description="Allocated resources")
    metrics: Optional[dict] = Field(None, description="Runtime metrics")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True