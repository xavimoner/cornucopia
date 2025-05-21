# crawler_rag/agents/extraction_tasks.py


"""
Contiene las instrucciones (prompts) para extraer automáticamente los campos de la base de datos 'convocatorias'.



Estos son los campos:
#	1. 	organismo
#	2. 	nombre
#	3. 	linea
#	4. 	fecha_inicio
#	5. 	fecha_fin
#	6. 	objetivo
#	7. 	beneficiarios
#	8. 	anio
#	9. 	area
#	10. 	presupuesto_minimo
#	11. 	presupuesto_maximo
#	12. 	duracion_minima
#	13. 	duracion_maxima
#	14. 	intensidad_de_subvencion
#	15. 	intensidad_de_prestamo
#	16. 	tipo_financiacion
#	17. 	forma_y_plazo_de_cobro
#	18. 	minimis
#	19. 	region_de_aplicacion
#	20. 	tipo_de_consorcio
#	21. 	costes_elegibles
#	22. 	dotacion_presupuestaria
#	23. 	numero_potencial_de_ayudas
#	24. 	tasa_de_exito
#	25. 	link_ficha_tecnica
#	26. 	link_orden_de_bases
#	27. 	link_convocatoria
#	28. 	link_plantilla_memoria
#	29. 	criterios_valoracion
#	30. 	documentacion_solicitud
#	31. 	created_at


"""



TASKS = {

    # 1. organismo
    "organismo": """Del texto a continuación, extrae el nombre del organismo que convoca o gestiona la ayuda.
Devuelve solo el nombre, sin introducciones ni frases explicativas.
Texto: {{TEXT}}""",

    # 2. nombre
    "nombre": """Extrae el nombre completo y oficial de la convocatoria, incluyendo el año si aparece.
Devuelve solo el nombre exacto, sin frases de introducción ni explicaciones.
Texto: {{TEXT}}""",

    # 3. linea
    "linea": """Indica si la convocatoria está incluida dentro de una línea o programa específico.
Devuelve solo el nombre del programa o 'No se menciona'.
Texto: {{TEXT}}""",

    # 4. fecha_inicio
    "fecha_inicio": """Extrae la fecha exacta (formato DD/MM/AAAA) a partir de la cual se pueden presentar solicitudes.
Devuelve solo la fecha. No incluyas frases como 'Según el texto...'.
Texto: {{TEXT}}""",

    # 5. fecha_fin
    "fecha_fin": """Extrae la fecha límite oficial para la presentación de solicitudes (formato DD/MM/AAAA).
Devuelve solo la fecha. No incluyas explicaciones ni referencias al texto.
Texto: {{TEXT}}""",

    # 6. objetivo
    "objetivo": """Resume el objetivo principal de la convocatoria en una o dos frases concisas.
Evita repeticiones o introducciones. Sé claro y directo.
Texto: {{TEXT}}""",

    # 7. beneficiarios
    "beneficiarios": """¿Quiénes pueden solicitar esta ayuda?
Devuelve una lista de perfiles separados por punto y coma. No incluyas frases como 'Según el texto...'.
Texto: {{TEXT}}""",

    # 8. anio
    "anio": """Indica el año de publicación o aplicación de la convocatoria.
Devuelve solo el número (ej: 2024).
Texto: {{TEXT}}""",

    # 9. area
    "area": """Indica el área temática o sector principal de la convocatoria (ej: I+D, digitalización, sostenibilidad).
Devuelve solo el nombre del área. No incluyas explicaciones.
Texto: {{TEXT}}""",

    # 10. presupuesto_minimo
    "presupuesto_minimo": """Indica si existe un presupuesto mínimo exigido por proyecto.
Devuelve solo la cifra en euros o 'No se especifica'. No incluyas frases adicionales.
Texto: {{TEXT}}""",

    # 11. presupuesto_maximo
    "presupuesto_maximo": """Indica el presupuesto máximo financiable por proyecto.
Devuelve solo la cifra en euros o 'Sin límite'. Evita frases introductorias.
Texto: {{TEXT}}""",

    # 12. duracion_minima
    "duracion_minima": """Extrae la duración mínima de los proyectos si se menciona.
Devuelve solo el valor numérico o en meses, sin frases adicionales.
Texto: {{TEXT}}""",

    # 13. duracion_maxima
    "duracion_maxima": """Extrae la duración máxima permitida para los proyectos subvencionados.
Devuelve solo el valor. No incluyas explicaciones.
Texto: {{TEXT}}""",

    # 14. intensidad_de_subvencion
    "intensidad_de_subvencion": """Indica los porcentajes de subvención aplicables y sus condiciones.
Devuelve los datos esenciales, en una lista si es posible. Evita frases explicativas.
Texto: {{TEXT}}""",

    # 15. intensidad_de_prestamo
    "intensidad_de_prestamo": """Si existen condiciones de préstamo, extrae los porcentajes, intereses o plazos.
Usa formato de lista si es aplicable. No incluyas frases como 'Según el texto...'.
Texto: {{TEXT}}""",

    # 16. tipo_financiacion
    "tipo_financiacion": """Indica si la financiación es subvención, préstamo o una combinación.
Devuelve solo una de las opciones. Evita frases explicativas.
Texto: {{TEXT}}""",

    # 17. forma_y_plazo_de_cobro
    "forma_y_plazo_de_cobro": """Describe cómo y cuándo se entrega el dinero al beneficiario.
Usa frases claras y directes. Formato esquemático si es llarg.
Texto: {{TEXT}}""",

    # 18. minimis
    "minimis": """Indica si la ayuda está sujeta al régimen de minimis.
Devuelve 'Sí', 'No' o 'No se menciona'.
Texto: {{TEXT}}""",

    # 19. region_de_aplicacion
    "region_de_aplicacion": """Indica el ámbito territorial de aplicación (ej: nacional, autonómico, Cantabria...).
Devuelve solo el nombre. No incluyas frases de contexto.
Texto: {{TEXT}}""",

    # 20. tipo_de_consorcio
    "tipo_de_consorcio": """Indica si la convocatoria permite o exige consorcios y de qué tipo.
Devuelve solo la estructura requerida o 'Individual'.
Texto: {{TEXT}}""",

    # 21. costes_elegibles
    "costes_elegibles": """Enumera los costes elegibles según la convocatoria.
Devuelve una lista separada por punto y coma.
Texto: {{TEXT}}""",

    # 22. dotacion_presupuestaria
    "dotacion_presupuestaria": """Indica la dotación total asignada a la convocatoria.
Devuelve solo la cifra (ej: 500.000 €). No incluyas frases como 'Según el texto...'.
Texto: {{TEXT}}""",

    # 23. numero_potencial_de_ayudas
    "numero_potencial_de_ayudas": """Indica si se menciona cuántos proyectos se espera financiar.
Devuelve el número o 'No se especifica'.
Texto: {{TEXT}}""",

    # 24. tasa_de_exito
    "tasa_de_exito": """Extrae el porcentaje de éxito si aparece.
Devuelve solo el valor numérico con símbolo (%), o 'No se menciona'.
Texto: {{TEXT}}""",

    # 25. link_ficha_tecnica
    "link_ficha_tecnica": """Extrae el enlace a la ficha técnica de la convocatoria.
Devuelve solo la URL.
Texto: {{TEXT}}""",

    # 26. link_orden_de_bases
    "link_orden_de_bases": """Extrae el enlace al documento de orden de bases si se menciona.
Devuelve solo la URL.
Texto: {{TEXT}}""",

    # 27. link_convocatoria
    "link_convocatoria": """Extrae el enlace oficial a la convocatoria publicada.
Devuelve solo la URL.
Texto: {{TEXT}}""",

    # 28. link_plantilla_memoria
    "link_plantilla_memoria": """Extrae el enlace a la plantilla de memoria técnica si aparece.
Devuelve solo la URL.
Texto: {{TEXT}}""",

    # 29. criterios_valoracion
    "criterios_valoracion": """Resume los criterios de valoración de la convocatoria.
Devuelve una lista o texto esquemático. Evita frases genéricas o introductòries.
Texto: {{TEXT}}""",

    # 30. documentacion_solicitud
    "documentacion_solicitud": """Enumera los documentos requeridos en la solicitud.
Devuelve una lista separada por punto y coma. No incluyas introducciones.
Texto: {{TEXT}}"""
}