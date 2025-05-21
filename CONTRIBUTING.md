<!--- CONTRIBUTING.md -->
# Guía de contribución al proyecto Cornucopia

Gracias por tu interés en contribuir a Cornucopia. Nuestro objetivo es que colaborar sea un proceso claro, ágil y útil tanto para quien propone como para quien revisa.

Por favor, sigue las siguientes pautas antes de enviar tu contribución.

---

## Cómo contribuir

1. Clona el repositorio en tu equipo local:
   ```bash
   git clone https://github.com/xavimoner/cornucopia.git
   cd cornucopia
   ```

2. Crea una nueva rama para tu funcionalidad o corrección:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```

3. Realiza tus cambios siguiendo el estilo del proyecto.

4. Verifica localmente que el sistema funciona correctamente:
   - La base de datos se puede inicializar (`db/init_db_schema.sql`)
   - Los scripts clave (`insert_documents_from_folder.py`, `unified_extraction_agent.py`) funcionan sin errores

5. Realiza un commit claro:
   ```bash
   git commit -m "Descripción breve del cambio"
   ```

6. Envía un Pull Request (PR) incluyendo:
   - Qué problema soluciona o qué funcionalidad añade
   - Qué partes del sistema afecta
   - Cómo probarlo si es necesario

---

## Estilo de código

- Utiliza **Python 3.10+**
- Sigue el estilo **PEP8**
- Usa nombres descriptivos para archivos, funciones y variables
- Incluye comentarios explicativos y, si es posible, un ejemplo de uso

Ejemplo de encabezado recomendado en scripts:

```python
"""
Script que vectoriza todos los documentos de una carpeta
Uso:
    python insert_documents_from_folder.py --subfolder "CDTI - PID"
"""
```

---

## Buenas prácticas

- Prefiere **commits pequeños y explicativos**
- Describe en el PR cualquier cambio en:
  - Estructura del proyecto
  - Dependencias (`requirements.txt`)
  - Variables de entorno necesarias
- No incluyas archivos temporales ni confidenciales:
  - `.env`
  - Carpetas `__pycache__/`, `logs/`, `vault/`

---

## Reportar errores o sugerencias

Para comunicar un error o proponer una mejora, abre un "Issue" en GitHub. Indica:

- Descripción clara del problema o propuesta
- Pasos para reproducirlo, si aplica
- Capturas de pantalla o ejemplos, si es posible

---

## Licencia

Al enviar una contribución, aceptas que tu código se licencie bajo la misma licencia del proyecto (MIT).

---

Gracias por ayudar a mejorar Cornucopia.
