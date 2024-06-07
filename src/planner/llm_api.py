#HERE put LLM Endpoint inside for OpenAI maybe langchain
import requests
import base64
import json
import openai
from prompts import prompts

from ui_components import UIComponents
# LLMEndpoint with direct access to OpenAI API

class LLMEndpoint:
    """
    Class to interact with the OpenAI API
    """
    def __init__(self, api_key, config_path):
        """
        Initialize the LLMEndpoint
        Args:
            api_key (str): OpenAI API key
            config_path (str): Path to the configuration file
        """
        self.api_key = api_key
        self.config_path = config_path
        openai.api_key = self.api_key
        self.endpoint_url = "https://api.openai.com/v1/chat/completions"

    def load_config(self):
        """
        Load the configuration file
        Returns:
            dict: Configuration file as dictionary
        """
        with open(self.config_path, 'r') as file:
            return json.load(file)

    def encode_image(self, image_path):
        """
        Encode an image to Base64
        Args:
            image_path (str): Path to the image file
        Returns:
            str: Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def encode_image_from_file(self, image_file):
        """
        Encode an image to Base64
        Args:
            image_file (file): Image file
        Returns:
            str: Base64 encoded image
        """
        return base64.b64encode(image_file.read()).decode('utf-8')

    def query(self, max_tokens=600, image_path=None):
        """
        Query the OpenAI API
        Args:
            max_tokens (int): Maximum number of tokens
            image_path (str): Path to the image file
        Returns:
            dict: Response from the OpenAI API
        """
        # config = self.load_config()
        messages = [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompts["dynamic_action_inference_prompt"]
          }
        ]
      }
    ]
        print("Dynamic action inference prompt:", prompts["dynamic_action_inference_prompt"])
        if image_path:
            base64_image = self.encode_image_from_file(image_path)
            # base64_image = self.encode_image(image_path) # for local testing
            image_message = {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
            messages.append(image_message)

        try:
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=max_tokens
            )
            response = response.choices[0].message.content.strip()
            print("Response from LLMEndpoint:", response)
            return json.loads(response)
        except Exception as e:
            return self.query()
            return {"error": str(e)}
        
# Example usage of LLMEndpoint
""" if __name__ == "__main__":
    api_key = "api-key" # do no push this to github!!
    config_path = '../promptconfig.json'
    endpoint = LLMEndpoint(api_key, config_path)
    response = endpoint.query(image_path="../protimemobile.png")
    gen = response.choices[0].message.content.strip()
    ui_componets = UIComponents(content=gen)
    print("Response:", str(ui_componets))
    #print("Response:", ui_componets.to_json()) 
    #print(gen) """
