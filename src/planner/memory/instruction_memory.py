class InstructionMemory:
  """
  This class represents the memory of the instructions.
  """
  def __init__(self, id, timestamp, instruction_text):
    self.id: float = id
    self.timestamp: float = timestamp
    self.instruction_text: str = instruction_text
    self.embedding: list[any] = []
    self.success: bool = False
    self.subtasks = list[SubtaskMemory]

class SubtaskMemory:
  """
  This class represents the memory of the subtasks.
  """
  def __init__(self, action_type, description, parameters) -> None:
    self.action_type = action_type
    self.description = description
    self.location = parameters[0]
    self.text = parameters[1]