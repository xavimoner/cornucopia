# process_pdf.py
import vllm
from deepseek import Deepseek
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from smolagents import SmolAgent  # Afegir SmolAgent per processar el text

# Inicialitzar vLLM
vllm_client = vllm.Client()

# Carregar el model Deepseek R1
model = Deepseek("/app/models/deepseek-r1")  # El model serà dins de /app/models

# Funció per llegir el PDF
def read_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Funció per processar el text amb Smolagents
def process_text_with_smolagents(text):
    agent = SmolAgent()
    result = agent.ask(text, question="Quins són els objectius del projecte?")
    return result

# Exemple de processament d'un PDF
pdf_path = "convocatoria.pdf"  # Camí del PDF descarregat

# Llegir el PDF
pdf_text = read_pdf(pdf_path)

# Processar el text amb Smolagents
result = process_text_with_smolagents(pdf_text)

# Mostrar el resultat
print("Resultat de Smolagents:", result)
