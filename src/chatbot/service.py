import json
import requests
import os
from urllib.parse import urljoin

api_url = "http://127.0.0.1:8000/"

def instruct(instruction, screens):
    """
    Send the instruction and the screens to the API.
    Args:
        instruction (str): The instruction.
        screens (dict): The screens.
    Returns:
        dict: The response from the API.
        int: The status code.
    """
    resp = requests.post(url=urljoin(api_url, "instruct"), data=instruction, files=screens)
    return resp.json(), resp.status_code