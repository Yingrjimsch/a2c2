import tiktoken


model2max_context = {
    "gpt-4": 7900,
    "gpt-4-0314": 7900,
    "gpt-3.5-turbo-0301": 3900,
    "gpt-3.5-turbo": 3900,
    "text-davinci-003": 4096,
    "text-davinci-002": 4096,
    "gpt-4o": 4096
}

class OutOfQuotaException(Exception):
    """
    Raised when the key has run out of quota.

    """
    def __init__(self, key, cause=None):
        super().__init__(f"No quota for key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        """
        Returns the error message with the cause if present.
        
        Returns:
            str: The error message.
        """
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

class AccessTerminatedException(Exception):
    """
    Raised when the key has been terminated.
    """
    def __init__(self, key, cause=None):
        super().__init__(f"Access terminated key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        """
        Returns the error message with the cause if present.
        
        Returns:
            str: The error message.
        """
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

def num_tokens_from_string(string: str, model_name: str) -> int:
    """
    Get the number of tokens in a string for a given model.
    
    Args:
        string (str): The string to encode.
        model_name (str): The model name.
        
    Returns:
            int: The number of tokens.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
