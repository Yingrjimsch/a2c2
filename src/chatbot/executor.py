##TODO pyautogui implementation
# Input example: ACTIONTYPE, COMPONENT, ADDITIONAL_INFO
# ACTIONTYPE = CLICK, TYPE, SCROLL,...,READ, --> ENUM oder so
#COMPONENT = (xyxy) --> bounding box (click on center of xyxy), (xy) -> directly click, --> image --> retrieve and click
#ADDITIONAL_INFO je nach ACTIONTYPE z.B. click braucht nichts oder vielleicht anzahl clicks, TYPE ADDITIONAL_INFO --> text

import pyautogui
from typing import Tuple, Union, Optional
from enum import Enum, auto

# Enum to represent the action type
class ActionType(Enum):
    """
    Enum to represent the action type
    CLICK: Click on a specific position on the screen
    DOUBLE_CLICK: Double click on a specific position on the screen
    TYPE: Type text on a specific position on the screen
    SCROLL: Scroll the screen
    READ: Read text from the screen
    LOCATE: Locate an image on the screen
    """
    CLICK = auto() # auto() is used to assign unique values to each member
    DOUBLE_CLICK = auto()
    TYPE = auto() 
    SCROLL = auto()
    READ = auto()  # read text from screen
    LOCATE = auto()  # locate an image on the screen

# Function to convert the JSON data to the corresponding action type, component, and additional info
def from_json(json_data: dict):
    """
    Convert the JSON data to the corresponding action type, component, and additional info
    Args:
        json_data (dict): JSON data containing the action type, component, and additional info
    Returns:
        Tuple[ActionType, Union[list[int, int], list[int, int, int, int], str], Optional[Union[int, str]]]: Tuple containing the action type, component, and additional info
    """
    action_type = ActionType[json_data["action_type"]]
    component = json_data["component"]
    if "additional_info" in json_data.keys():
        print("There are additional infos")
        additional_info = json_data["additional_info"]
    else:
        additional_info = ""
    return action_type, component, additional_info

# Function to execute the action based on the action type, component, and additional info
def execute_action(action_type: ActionType, component: Union[list[int, int], list[int, int, int, int], str], additional_info: Optional[Union[int, str]] = None):
    """
    Execute the action based on the action type, component, and additional info
    Args:
        action_type (ActionType): Action type
        component (Union[list[int, int], list[int, int, int, int], str]): Component to perform the action
        additional_info (Optional[Union[int, str]]): Additional information for the action  
    """
    if isinstance(component, list):
        if len(component) == 2:
            # Clicks, when component is a tuple of 2 integers
            x, y = component
            x = x * 1.40625
            y = y * 1.40625
        elif len(component) == 4:
            # Click on center, when component is a tuple of 4 integers (bounding box)
            x1, y1, x2, y2 = component
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            x = x * 1.40625
            y = y * 1.40625
        elif len(component) == 0:
            x, y = 0,0
        else:
            raise ValueError("Ungültiges Format für Komponente")

        # Execute the action based on the action type
        if action_type == ActionType.CLICK:
            clicks = additional_info if additional_info else 1
            pyautogui.click(x, y, clicks=clicks, interval=0.25, duration=2)
        elif action_type == ActionType.DOUBLE_CLICK:
            pyautogui.doubleClick(x, y, interval=0.25)
        elif action_type == ActionType.SCROLL:
            distance = additional_info if additional_info else 0
            pyautogui.scroll(distance, x, y, interval=0.25)
        elif action_type == ActionType.READ:
            print(f"Read at position ({x}, {y})")
        elif action_type == ActionType.TYPE:
            text = additional_info if additional_info else ""
            pyautogui.click(x, y, interval=0.25)  # click to focus on the text field
            pyautogui.typewrite(text, interval=0.25) # type the text
        elif action_type == ActionType.LOCATE:
            searchComponent = additional_info if additional_info else ""
            # bounding box of the located component
            x1, y1, width, height = pyautogui.locateOnScreen(searchComponent)
            # center of the located component
            x = x1 + width // 2
            y = y1 + height // 2
            pyautogui.doubleClick(x, y, interval=0.25)
    else:
        raise ValueError("Ungültige Eingabe für Komponente oder ActionType")
    
# Function to get the current mouse coordinates
def get_coordinates():
        """ 
        Get the current mouse coordinates
        Returns:
            Tuple[int, int]: Tuple containing the x and y coordinates of the mouse
        """
        return pyautogui.position()
    
# Test the functions
""" if __name__ == "__main__":
    # test the from_json function
    json_data = {
        "action_type": "CLICK",
        "component": [164, 935],
        "additional_info": 1
    }
    print("before json", json_data)
    action_type, component, additional_info = from_json(json_data)
    print("after json", from_json(json_data))
    # Test the execute_action function
    print(get_coordinates())
    # Click on the center of the screen
    #execute_action(action_type, component, additional_info) """
