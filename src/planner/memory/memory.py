import json
from memory.instruction_memory import InstructionMemory
import numpy as np
import openai
import os

openai.api_key = 'OPENAI_APIKEY' # do no push this to github!!

class Memory:  
  """
  This class is responsible for the memory of the instructions.
  """
  def __init__(self, location):
    self.location = location
    self.embedding_fn = self.embed
    self.memory = self.load()
    
  def euclidean_distance(a, b):
    """
    Calculate the euclidean distance between two vectors.
    
    Args:
        a (list): The first vector.
        b (list): The second vector.
          
    Returns:
        float: The euclidean distance between the two vectors.
    """
    return 1 - np.linalg.norm(np.array(a) - np.array(b))

  def cosine_similarity(a, b):
    """
    Calculate the cosine similarity between two vectors.

    Args:
        a (list): The first vector.
        b (list): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

  def embed(self, instruction: str, embedding_model: str = "text-embedding-ada-002"):
    """
    Embed a line of text.
      
      Args:
      
        instruction (str): The instruction to be embedded.
        embedding_model (str): The embedding model to use.
        
      Returns:
        
        list: The embedded instruction.
    """
    # Embed a line of text TODO auslagern nach rebekka logik
    response = openai.embeddings.create(
        model=embedding_model,
        input=instruction
    )
    embedding = response.data[0].embedding
    return embedding

  def load(self):
    """
    Load the memory from the file.
      
      Returns:
        
        list: The memory.
    """
    if not os.path.exists(self.location):
      with open(self.location, "w") as f:
        json.dump([], f)
        print(f"File {self.location} created with an empty JSON object")
    with open(self.location, 'r') as f:
      instructions = json.load(f)
      print(f"File {self.location} loaded as memory with {len(instructions)} entries")
    return instructions
  
  def get_filtered_memory(self, metadata: str):
    """
    Get the memory filtered by metadata.
      
      Args:
      
        metadata (str): The metadata to filter by.
        
      Returns:
        
        list: The filtered memory.
    """
    return [mem for mem in self.memory if all(item in mem.metadata.items() for item in metadata.items())]
  
  def compare_embeddings(self, instruction_embedding, min_similarity_score, memory, similarity_fn=cosine_similarity):
    """
    Compare the embeddings of the instruction with the memory.
      
      Args:
      
        instruction_embedding (list): The embedded instruction.
        min_similarity_score (float): The minimum similarity score.
        memory (list): The memory.
        similarity_fn (function): The similarity function.
        
      Returns:
        
        list: The similarities.
    """
    similarities = []
    for ee in memory:
        print(ee)
        print(instruction_embedding)
        similarity = similarity_fn(instruction_embedding, ee['embedding'])
        if similarity < min_similarity_score:
          break
        similarities.append((ee, similarity_fn(instruction_embedding, ee['embedding'])))
    return sorted(similarities, key=lambda chunk: chunk[1], reverse=True)
  
  def get_top_results(self, instruction: InstructionMemory, k=2, metadata: dict = {}, min_similarity_score=.8):
    """ 
    Get the top k results from the memory.
      
      Args:
      
        instruction (InstructionMemory): The instruction to search for.
        k (int): The number of results.
        metadata (dict): The metadata to filter by.
        min_similarity_score (float): The minimum similarity score.
        
      Returns:
        
        list: The top k results.
    """
    embedded_instruction = self.embed(instruction)
    similarities = self.compare_embeddings(embedded_instruction, min_similarity_score, self.get_filtered_memory(metadata))
    return similarities[:k]
  
  def save(self):
    """ 
    Save the memory to the file.
    
    """
    with open(self.location, 'w') as f:
        json.dump(self.memory, f, indent=4)

  def add(self, instruction: InstructionMemory):
    """
    Add an instruction to the memory.
      
      Args:
      
        instruction (InstructionMemory): The instruction to be added.
    """
    instruction.embedding = self.embed(instruction)
    self.memory.append(instruction.__dict__)
    self.save()
  