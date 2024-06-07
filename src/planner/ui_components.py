import json
import re


class UIComponent:
    """
    Represents a UI component with its type, coordinates, and action description.
    """
    def __init__(self, component_type, coordinates, action_description):
        self.component_type = component_type
        self.coordinates = coordinates
        self.action_description = action_description

    def __str__(self):
        """
        Returns a string representation of the UI component.
        Returns:
            str: A string representation of the UI component.
        """
        return f"{self.component_type} at {self.coordinates} '{self.action_description}'"

    def to_json(self):
        """
        Returns the UI component as a JSON string.
        Returns:
            str: The UI component as a JSON string.
        """
        return json.dumps({
            "component_type": self.component_type,
            "coordinates": self.coordinates,
            "action_description": self.action_description
        })

class UIComponents:
    """
    Represents a collection of UI components.
    Args:
        content (str): The content of the response.
    Attributes:
        components (List[UIComponent]): The list of UI components.
        
    """
    def __init__(self, content):
        """
        Initializes the UIComponents object.
        Args:
            content (str): The content of the response. 
        """
        #cleaned_content = self.clean_content(content)
        # Hier extrahieren wir den relevanten Content aus der Response
        # Entfernen der Backticks, die den JSON-String umschließen und Trimmen der Zeichenketten
        # In diesem Fall gibt es keine Backticks in Ihrem Beispiel, daher laden wir direkt
        #components_data = json.loads(cleaned_content)
        self.components = [UIComponent(**component) for component in content]
        
    def __str__(self):
        """
        Returns a string representation of the UI components.
        Returns:
            str: A string representation of the UI components.
        """
        return "\n".join(str(component) for component in self.components)

    def to_json(self):
        """
        Returns the UI components as a JSON string.
        Returns:
            str: The UI components as a JSON string.
        """
        return json.dumps([json.loads(component.to_json()) for component in self.components])
    
    def clean_content(self, content):
        """
        Cleans the content of the response by removing the surrounding backticks.
        Args:
            content (str): The content of the response.
        Returns:
            str: The cleaned content.
        """
        cleaned_content = re.sub(r'^```json|```$', '', content, flags=re.MULTILINE).strip()
        return cleaned_content
    
# for testing
#gen = '[{"component_type": "Back Button", "coordinates": [10, 10], "action_description": "Navigate to the previous page"},{"component_type": "Back Button", "coordinates": [10, 10], "action_description": "Navigate to the previous page"}]'

#ui_components = UIComponents(content=gen)
#print("Response:", str(ui_components))