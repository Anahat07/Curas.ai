from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, field_validator
from .enums import WorkflowState


class PatientCreate(BaseModel):
    fhir_id: str
    mrn: str
    display_name: str
    date_of_birth: date
    physician_id: UUID


class PatientUpdate(BaseModel):
    display_name: str | None = None
    workflow_state: WorkflowState | None = None


class Patient(BaseModel):
    id: UUID
    fhir_id: str
    mrn: str
    display_name: str
    date_of_birth: date
    physician_id: UUID
    workflow_state: WorkflowState | None = None  # Make optional with None default
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
    
    @field_validator("workflow_state", mode="before")
    @classmethod
    def default_workflow_state(cls, v):
        """Default to PENDING if workflow_state is None or missing"""
        if v is None or v == "":
            return WorkflowState.PENDING
        return v