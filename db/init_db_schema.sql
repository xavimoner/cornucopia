-- db/init_db_schema.sql
-- Crea la taula de convocatòries

CREATE TABLE IF NOT EXISTS convocatorias (
    id SERIAL PRIMARY KEY,
    organismo TEXT,
    nombre TEXT,
    linea TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    objetivo TEXT,
    beneficiarios TEXT,
    anio TEXT,
    area TEXT,
    presupuesto_minimo TEXT,
    presupuesto_maximo TEXT,
    duracion_minima TEXT,
    duracion_maxima TEXT,
    intensidad_de_subvencion TEXT,
    intensidad_de_prestamo TEXT,
    tipo_financiacion TEXT,
    forma_y_plazo_de_cobro TEXT,
    minimis TEXT,
    region_de_aplicacion TEXT,
    tipo_de_consorcio TEXT,
    costes_elegibles TEXT,
    dotacion_presupuestaria TEXT,
    numero_potencial_de_ayudas TEXT,
    tasa_de_exito TEXT,
    link_ficha_tecnica TEXT,
    link_orden_de_bases TEXT,
    link_convocatoria TEXT,
    link_plantilla_memoria TEXT,
    criterios_valoracion TEXT,
    documentacion_solicitud TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crea la taula de documents vectoritzats (text sencer)
CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    convocatoria_id INTEGER REFERENCES convocatorias(id) ON DELETE CASCADE,
    fuente TEXT NOT NULL, -- Ex: "web", "pdf"
    url TEXT,
    titulo TEXT,
    texto TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
