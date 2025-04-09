from smolagents import tool
from typing import Dict

@tool
def extract_variables(content: str, data: Dict[str, str]) -> Dict[str, str]:
    """
    Test tool that takes a text input and a dictionary, then returns the dictionary.

    Args:
        content (str): A sample text input.
        data (Dict[str, str]): A dictionary containing key-value pairs.

    Returns:
        Dict[str, str]: The same dictionary provided as input.
    """
    print("Content received:", content[:100])  # Mostramos solo los primeros 100 caracteres
    return data

print("Tool defined and working")

