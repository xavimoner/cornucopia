# backend/formatters.py
def format_response(query: str, result: str):
    return {
        "input": query,
        "output": result,
        "format": "markdown"
    }
