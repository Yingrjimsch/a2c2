from pydantic import BaseModel, model_validator
from uuid import uuid4, UUID
import time
import json

time.time()
class Instruction(BaseModel):
    """
    The Instruction class.
    """
    id: UUID = uuid4()
    instruction_text: str | None = None
    error_message: str | None = None
    subtask_pointer: int = 0
    subinstructions_pointer: int = 0
    subinstructions: list = ['No instruction']
    subtasks: list = []
    timestamp: float = time.time()
    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        """
        Validate the instruction to be JSON.
        
        Args:
            value (Instruction): The instruction.
            
        Returns:
                Instruction: The instruction.
        """
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value