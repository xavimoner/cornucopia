# agents/extraction_agent.py

import os
from smolagents import CodeAgent, HfApiModel

# Load task definition amb descriptor de ccamps
from instructions.cdti_extraction_task import task

# Custom tools per accedir  i processasr text local
from agents.text_extraction_tools import (
    read_pdf_text,
    read_web_text,
    extract_field,
    extract_multiple_fields
)

# ────────────────────────────────────────────────────────────────────────────────
# Load the model
# ────────────────────────────────────────────────────────────────────────────────
model = HfApiModel(model_id="meta-llama/Llama-3.3-70B-Instruct")

# ────────────────────────────────────────────────────────────────────────────────
# Prompt for reasoning and extraction
# ────────────────────────────────────────────────────────────────────────────────
prompt = """
You are an expert data extraction agent.

You are given access to preprocessed text from web pages and PDFs.
You MUST ONLY use the available tools to extract structured information.

Available tools:
- read_pdf_text()
- read_web_text()
- extract_field(field_name)
- extract_multiple_fields(list_of_fields)

▸ Start by reading the content using read_pdf_text() and/or read_web_text().
▸ Then extract the requested information by calling extract_field("field") or extract_multiple_fields([...]).
▸ Output all information as a dictionary (JSON-style).

DO NOT write parsing code manually.
DO NOT use regex or string manipulation.
DO NOT reimplement logic.

Always follow this format:

Thought: what are you trying to extract?
Code:
```py
# your code
```<end_code>

Observation: result of the tool call
"""

# ────────────────────────────────────────────────────────────────────────────────
# Agent definition
# ────────────────────────────────────────────────────────────────────────────────
agent = CodeAgent(
    tools=[
        read_pdf_text,
        read_web_text,
        extract_field,
        extract_multiple_fields,
    ],
    model=model,
    prompt_templates={
        "system_prompt": prompt,
        "final_answer": {
            "pre_messages": "Extraction complete. Result:",
            "post_messages": "End of extraction."
        }
    },
    verbosity_level=2,
)

# ────────────────────────────────────────────────────────────────────────────────
# Execute agent with task
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = agent.run(task)
    print("\n🟢 Final extracted data:")
    print(result)
