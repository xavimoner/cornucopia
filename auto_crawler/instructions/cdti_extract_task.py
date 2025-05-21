# instructions/cdti_extraction_task.py

task = """
Lee los textos extraídos de la página web (webpage_text.txt) y del PDF (pdf_text.txt).
A partir de esta información, intenta completar automáticamente los siguientes campos.

Para cada campo, busca la mejor información disponible y complétala con claridad y concisión. Si no se encuentra, deja el campo en blanco o escribe "Desconocido".

Campos a completar:
- organismo: Nombre del organismo que concede la ayuda.
- nombre: Título completo de la convocatoria.
- línea: Línea o programa de ayuda al que pertenece.
- fecha_inicio: Fecha de apertura de la convocatoria.
- fecha_fin: Fecha límite para presentar solicitudes.
- objetivo: Objetivo principal de la ayuda o del proyecto financiable.
- beneficiarios: Quién puede optar a esta ayuda (tipos de empresas, entidades, etc.).
- anio: Año natural o ejercicio presupuestario al que pertenece.
- area: Área temática o sector de aplicación.
- presupuesto_minimo: Presupuesto mínimo admitido por proyecto.
- presupuesto_maximo: Presupuesto máximo admisible.
- duracion_minima: Duración mínima del proyecto subvencionable.
- duracion_maxima: Duración máxima del proyecto.
- intensidad_de_subvencion: Porcentaje de subvención (ej: 70%).
- intensidad_de_prestamo: Porcentaje o importe máximo del préstamo.
- tipo_financiacion: Si es subvención, préstamo, ayuda reembolsable, etc.
- forma_y_plazo_de_cobro: Cuándo y cómo se cobra la ayuda.
- minimis: Si está sujeta a régimen de minimis (Sí/No).
- region_de_aplicacion: Comunidad Autónoma o zona donde aplica.
- tipo_de_consorcio: Si se exige consorcio o cooperación (y de qué tipo).
- costes_elegibles: Qué gastos pueden financiarse.
- dotacion_presupuestaria: Dotación total asignada a la convocatoria.
- numero_potencial_de_ayudas: Número estimado de ayudas a conceder.
- tasa_de_exito: Porcentaje aproximado de proyectos aprobados.
- link_ficha_tecnica: Enlace a la ficha oficial.
- link_orden_de_bases: Enlace a la orden de bases.
- link_convocatoria: Enlace a la convocatoria.
- link_plantilla_memoria: Enlace a la plantilla de memoria.
- criterios_valoracion: Criterios de selección y valoración.
- documentacion_solicitud: Documentos necesarios para presentar la solicitud.

IMPORTANTE:
▸ Utiliza la información tanto de la web como del PDF.
▸ No repitas párrafos largos: resume.
▸ Mantén formatos coherentes como fechas (DD/MM/AAAA), porcentajes, enlaces completos, etc.
▸ Los enlaces deben comenzar por "http" si están disponibles.
▸ Si un dato no se puede extraer, indica "Desconocido".

Cuando termines, muestra todos los campos con el valor que hayas asignado a cada uno.
"""


