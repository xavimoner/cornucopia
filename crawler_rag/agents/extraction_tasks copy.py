# crawler_rag/agents/extraction_tasks.py



"""
Conté la definició dels prompts per extreure informació per a cada camp de la taula 'convocatorias'.
Cada entrada inclou el nom del camp i la instrucció (prompt) corresponent.

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
#


TASKS = [

    # 1. organismo
    {
        "field": "organismo",
        "prompt": """Extrae el nombre del organismo que convoca o gestiona la ayuda. 
Puede ser un ministerio, agencia, consejería, fundación o similar. Devuelve solo el nombre más relevante tal como aparece en el texto.

Texto:
{{TEXT}}"""
    },

    # 2. nombre
    {
        "field": "nombre",
        "prompt": """Extrae el nombre completo y oficial de la convocatoria. 
Incluye el año si aparece. Devuelve el nombre más reconocible tal como aparece en el documento.

Texto:
{{TEXT}}"""
    },

    # 3. linea
    {
        "field": "linea",
        "prompt": """Indica si la convocatoria está incluida dentro de alguna línea o programa específico. 
Por ejemplo: Línea Directa de Innovación, Línea NEOTEC, Línea de Financiación Verde...

Texto:
{{TEXT}}"""
    },

    # 4. fecha_inicio
    {
        "field": "fecha_inicio",
        "prompt": """Indica la fecha a partir de la cual se pueden presentar solicitudes. 
Si hay varias fechas, devuelve la más próxima a hoy.

Texto:
{{TEXT}}"""
    },

    # 5. fecha_fin
    {
        "field": "fecha_fin",
        "prompt": """Indica la fecha límite de presentación de solicitudes. 
Si hay una prórroga prevista, ignórala y devuelve solo la fecha oficial.

Texto:
{{TEXT}}"""
    },

    # 6. objetivo
    {
        "field": "objetivo",
        "prompt": """Resume el objetivo principal de la convocatoria en una o dos frases. 
Qué pretende fomentar o financiar: investigación, contratación, internacionalización, eficiencia energética, etc.

Texto:
{{TEXT}}"""
    },

    # 7. beneficiarios
    {
        "field": "beneficiarios",
        "prompt": """¿Quiénes pueden solicitar esta ayuda? 
Extrae el perfil de beneficiarios (ej: PYMEs, grandes empresas, asociaciones, universidades, emprendedores...). 
Devuelve una lista separada por punto y coma.

Texto:
{{TEXT}}"""
    },

    # 8. anio
    {
        "field": "anio",
        "prompt": """Indica el año de publicación o aplicación de la convocatoria.

Texto:
{{TEXT}}"""
    },

    # 9. area
    {
        "field": "area",
        "prompt": """Indica el área temática o sector al que se dirige la ayuda. 
Por ejemplo: I+D, energía, digitalización, emprendimiento, salud, etc.

Texto:
{{TEXT}}"""
    },

    # 10. presupuesto_minimo
    {
        "field": "presupuesto_minimo",
        "prompt": """Indica si hay un presupuesto mínimo exigido por proyecto o entidad participante. 
Si hay diferentes condiciones por tipo de empresa, especifícalas brevemente.

Texto:
{{TEXT}}"""
    },

    # 11. presupuesto_maximo
    {
        "field": "presupuesto_maximo",
        "prompt": """Indica el presupuesto máximo financiable por proyecto o entidad. 
Si no hay límite, especifica 'Sin límite (orientativo: X €)' si se menciona alguna referencia.

Texto:
{{TEXT}}"""
    },

    # 12. duracion_minima
    {
        "field": "duracion_minima",
        "prompt": """Indica la duración mínima de los proyectos financiables, si se especifica.

Texto:
{{TEXT}}"""
    },

    # 13. duracion_maxima
    {
        "field": "duracion_maxima",
        "prompt": """Indica la duración máxima permitida del proyecto o ayuda.

Texto:
{{TEXT}}"""
    },

    # 14. intensidad_de_subvencion
    {
        "field": "intensidad_de_subvencion",
        "prompt": """Describe los porcentajes de subvención aplicables. 
Incluye variaciones por tipo de empresa (pequeña, mediana, grande) si se especifican.

Texto:
{{TEXT}}"""
    },

    # 15. intensidad_de_prestamo
    {
        "field": "intensidad_de_prestamo",
        "prompt": """Describe las condiciones del préstamo si existen: % financiado, tipo de interés, carencia, plazo de amortización, tramo no reembolsable, etc.

Texto:
{{TEXT}}"""
    },

    # 16. tipo_financiacion
    {
        "field": "tipo_financiacion",
        "prompt": """Indica el tipo de financiación: subvención, préstamo, combinación de ambos...

Texto:
{{TEXT}}"""
    },

    # 17. forma_y_plazo_de_cobro
    {
        "field": "forma_y_plazo_de_cobro",
        "prompt": """Describe cómo y cuándo se entrega el dinero al beneficiario: anticipos, pagos por hitos, por anualidades...

Texto:
{{TEXT}}"""
    },

    # 18. minimis
    {
        "field": "minimis",
        "prompt": """Indica si la ayuda está sujeta al régimen de minimis. 
Devuelve 'Sí', 'No' o 'No se menciona'.

Texto:
{{TEXT}}"""
    },

    # 19. region_de_aplicacion
    {
        "field": "region_de_aplicacion",
        "prompt": """Indica el ámbito territorial de aplicación: nacional, autonómico, o provincias específicas. 
Ej: Andalucía, País Vasco, Comunitat Valenciana...

Texto:
{{TEXT}}"""
    },

    # 20. tipo_de_consorcio
    {
        "field": "tipo_de_consorcio",
        "prompt": """Si se permite o exige cooperación, describe el tipo de consorcio requerido (mínimo de entidades, requisitos de participación, etc.). 
Si es individual, indícalo también.

Texto:
{{TEXT}}"""
    },

    # 21. costes_elegibles
    {
        "field": "costes_elegibles",
        "prompt": """Enumera los principales costes subvencionables: personal, subcontratación, maquinaria, patentes, software, etc. 
Devuelve una lista separada por punto y coma.

Texto:
{{TEXT}}"""
    },

    # 22. dotacion_presupuestaria
    {
        "field": "dotacion_presupuestaria",
        "prompt": """Indica el presupuesto total asignado a la convocatoria si se menciona. 
Ej: 50 M€, 12,5 millones...

Texto:
{{TEXT}}"""
    },

    # 23. numero_potencial_de_ayudas
    {
        "field": "numero_potencial_de_ayudas",
        "prompt": """Indica si se menciona cuántos proyectos se espera financiar. 
Devuelve un número aproximado o 'No se especifica'.

Texto:
{{TEXT}}"""
    },

    # 24. tasa_de_exito
    {
        "field": "tasa_de_exito",
        "prompt": """Indica el porcentaje de éxito esperado o pasado si aparece. 
Ej: 40 %, 75 %, etc.

Texto:
{{TEXT}}"""
    },

    # 25. link_ficha_tecnica
    {
        "field": "link_ficha_tecnica",
        "prompt": """Extrae el enlace a la ficha técnica de la convocatoria si aparece en el texto.

Texto:
{{TEXT}}"""
    },

    # 26. link_orden_de_bases
    {
        "field": "link_orden_de_bases",
        "prompt": """Extrae el enlace al documento de orden de bases si se proporciona.

Texto:
{{TEXT}}"""
    },

    # 27. link_convocatoria
    {
        "field": "link_convocatoria",
        "prompt": """Extrae el enlace oficial a la convocatoria publicada (web, BOE, etc.).

Texto:
{{TEXT}}"""
    },

    # 28. link_plantilla_memoria
    {
        "field": "link_plantilla_memoria",
        "prompt": """Extrae el enlace a la plantilla o modelo de memoria técnica si se proporciona.

Texto:
{{TEXT}}"""
    },

    # 29. criterios_valoracion
    {
        "field": "criterios_valoracion",
        "prompt": """Resume los criterios de evaluación o valoración aplicables a la convocatoria. 
Indica puntuaciones, pesos o categorías si aparecen.

Texto:
{{TEXT}}"""
    },

    # 30. documentacion_solicitud
    {
        "field": "documentacion_solicitud",
        "prompt": """Enumera los documentos que se deben presentar en la solicitud: cuestionario, memoria, certificados, etc. 
Devuelve una lista separada por punto y coma.

Texto:
{{TEXT}}"""
    }
]
