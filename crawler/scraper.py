# crawler/scraper.py

from smolagents import tool
from typing import Dict

@tool
def extract_variables(content: str, title_variable_map: dict) -> dict:
    """
    Extracts specific variables from the given content based on a title-variable mapping.

    Args:
        content (str): The full text from which variables should be extracted.
        title_variable_map (dict): A dictionary mapping section titles to variable names.
            - Keys (str): Titles appearing in the content.
            - Values (str): The corresponding variable names where extracted text will be stored.

    Returns:
        dict: A dictionary with extracted values.
            - Keys correspond to variable names in `title_variable_map`.
            - Values contain the extracted text from the content.

    Example:
        ```json
        {
            "content": "Actuación: Proyectos I+D\\nFecha de inicio: 01/01/2022\\nBeneficiarios: Empresas",
            "title_variable_map": {
                "Actuación": "nombre",
                "Fecha de inicio": "fecha_inicio"
            }
        }
        ```
        Output:
        ```json
        {
            "nombre": "Proyectos I+D",
            "fecha_inicio": "01/01/2022"
        }
        ```
    """
    extracted_data = {}
    for title, variable in title_variable_map.items():
        start_index = content.find(title)
        if start_index != -1:
            extracted_data[variable] = content[start_index + len(title):].split('\n')[0].strip()
    return extracted_data
