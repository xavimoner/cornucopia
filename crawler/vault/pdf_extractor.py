from smolagents import CodeAgent
from PyPDF2 import PdfReader
import os

# Definimos el agente para extraer información de un PDF
class AgenteExtraccionPDF(CodeAgent):
    def extraer_info_de_pdf(self, ruta_pdf):
        """Extrae información relevante del PDF."""
        if not os.path.exists(ruta_pdf):
            return "Error: El archivo PDF no existe."
        
        with open(ruta_pdf, "rb") as file:
            lector = PdfReader(file)
            texto = "\n".join([pagina.extract_text() for pagina in lector.pages if pagina.extract_text()])
        
        # Pasar el texto extraído a vLLM para obtener información estructurada
        datos_estructurados = self.procesar_con_vllm(texto)
        return datos_estructurados
    
    def procesar_con_vllm(self, texto):
        """Envía el texto a vLLM para su procesamiento."""
        from vllm import Client
        cliente = Client("http://vllm:5000")  # Conexión con el contenedor vLLM
        
        prompt = (
            "Extrae los siguientes datos de la siguiente convocatoria de subvención:\n"
            "- organismo\n"
            "- nombre\n"
            "- línea\n"
            "- fecha inicio\n"
            "- fecha_fin\n"
            "- objetivo\n"
            "- beneficiarios\n"
            "- anio\n"
            "- area\n"
            "- presupuesto_minimo\n"
            "- presupuesto_maximo\n"
            "- duración_minima\n"
            "- duración_maxima\n"
            "- intensidad_de_subvención\n"
            "- intensidad_de_prestamo\n"
            "- tipo_financiacion\n"
            "- forma_y_plazo_de_cobro\n"
            "- Minimis\n"
            "- Region_de_aplicación\n"
            "- Tipo_de_consorcio\n"
            "- costes_elegibles\n"
            "- dotacion_presupuestaria\n"
            "- numero_potencial_de_ayudas\n"
            "- tasa_de_exito\n"
            "- link_ficha_técnica\n"
            "- link_orden_de_bases\n"
            "- link_convocatoria\n"
            "- link_plantilla_memoria\n"
            "- criterios_valoración\n"
            "- documentacion_solicitud\n\n"
            f"Convocatoria: {texto}"
        )
        
        respuesta = cliente.generate(prompt, max_tokens=500)
        return respuesta["text"]

# Ejemplo de uso
if __name__ == "__main__":
    agente = AgenteExtraccionPDF()
    ruta_pdf = "convocatoria.pdf"  # PDF descargado por el crawler
    datos_extraidos = agente.extraer_info_de_pdf(ruta_pdf)
    print("Datos extraídos:", datos_extraidos)
