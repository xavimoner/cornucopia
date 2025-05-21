-- db/init_db_schema.sql

\echo 'SCRIPT: Iniciant init_db_schema.sql - Creant taules...'

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
\echo 'SCRIPT: Taula convocatorias creada (o ja existia).'

CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    convocatoria_id INTEGER REFERENCES convocatorias(id) ON DELETE CASCADE,
    fuente TEXT NOT NULL,
    url TEXT,
    titulo TEXT,
    texto TEXT,
    embedding vector(1536), -- Assegura't que la dimensió coincideixi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\echo 'SCRIPT: Taula documentos creada (o ja existia).'

\echo 'SCRIPT: Creant taula usuaris...'
CREATE TABLE IF NOT EXISTS usuaris (
    id SERIAL PRIMARY KEY,
    nom_usuari VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    nom_complet VARCHAR(255),
    rol VARCHAR(50) NOT NULL DEFAULT 'usuari',
    actiu BOOLEAN DEFAULT TRUE,
    data_creacio TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
\echo 'SCRIPT: Taula usuaris creada (o ja existia).'

-- Opcional: Índexos addicionals: pel futur
-- CREATE INDEX IF NOT EXISTS idx_usuaris_email ON usuaris (email);