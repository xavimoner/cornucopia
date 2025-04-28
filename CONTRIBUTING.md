# Guía de contribución a Cornucopia

Gracias por tu interés en contribuir al proyecto Cornucopia. Queremos que colaborar sea un proceso claro y ordenado.

Por favor, sigue estas pautas:

---

## ¿Cómo contribuir?

1. **Clona el repositorio** en tu máquina local.
2. **Crea una nueva rama** para tu funcionalidad o corrección de errores:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
3. **Haz tus cambios** siguiendo el estilo de codificación del proyecto.
4. **Prueba tus cambios** antes de enviar.
5. **Realiza un commit claro**:
   ```bash
   git commit -m "Descripción breve del cambio"
   ```
6. **Envía un Pull Request** (PR) describiendo:
   - Qué problema soluciona
   - Qué mejoras incluye
   - Instrucciones si es necesario hacer alguna prueba especial

---

## Estilo de codificación

- Usa **Python 3.10+**.
- Sigue el estilo **PEP8** (puedes comprobarlo con `flake8` si quieres).
- Utiliza **nombres descriptivos** para archivos, funciones y variables.
- Los scripts deben incluir:
  - Comentarios al principio indicando su funcionalidad.
  - Si es posible, ejemplos de uso en un bloque de texto.

---

## Pruebas

Antes de enviar cambios importantes:
- Asegúrate de que la base de datos se puede inicializar correctamente (`db/init_db_schema.sql`).
- Verifica que los scripts principales (`insert_documents_from_folder.py`, `unified_extraction_agent.py`) funcionan sin errores.

---

## Buenas prácticas

- **Pequeños commits** son mejores que grandes cambios no documentados.
- **Explica claramente** en el PR cualquier cambio en dependencias (`requirements.txt`) o en la estructura del proyecto.
- **Evita** incluir archivos temporales, logs o credenciales (`.env`, carpetas `logs/`, `__pycache__/`, etc.).

---

## Reportar errores o sugerencias

Si encuentras un error o quieres proponer una mejora:
- Abre un "Issue" en GitHub describiendo claramente el problema o la propuesta.

---

## Licencia

Al contribuir, aceptas que tu código se licencie bajo la misma licencia del proyecto Cornucopia.

---

¡Gracias por hacer de Cornucopia un proyecto mejor!
