from fastapi import FastAPI, File, HTTPException, UploadFile, Body
from typing import List
from dto.instruction_dto import Instruction
from planner_logic import plan

# mocked action as a JSON in the Format (ActionType, Component, Additional_Info):
mocked_action = {
    "action_type": "CLICK",
    "component": [144, 926],
    "additional_info": 1
}

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/instruct")
async def instruct(instruction: Instruction = Body(...), screens: List[UploadFile] = File(...)):
    try:
        # Versucht, eine Instruktion zu planen
        planned_instruction = plan(instruction, screens)
        if planned_instruction is None:
            return "No more subinstructions to execute. Please enter next instruction."
        
        # Falls eine Instruktion zurückgegeben wurde
        print(planned_instruction.instruction_text)
        print("Uploaded Files:", [screen.filename for screen in screens])
        print("Subtasks are:", planned_instruction.subtasks)
        
        return planned_instruction
    
    except Exception as e:
        # Loggen des Fehlers und Rückgabe einer Fehlermeldung
        print(f"En error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while planning the instruction")
