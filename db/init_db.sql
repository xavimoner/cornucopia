-- db/init_db.sql
-- Activem l'extensió pgvector (només si no està activada)
CREATE EXTENSION IF NOT EXISTS vector;

-- Creem la taula de dades estructurades de convocatòries
CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,
    organismo VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    linea VARCHAR(255),
    fecha_inicio DATE,
    fecha_fin DATE,
    objetivo TEXT,
    beneficiarios TEXT,
    anio INTEGER,
    area VARCHAR(255),
    presupuesto_minimo DECIMAL(15,2),
    presupuesto_maximo DECIMAL(15,2),
    duracion_minima VARCHAR(50),
    duracion_maxima VARCHAR(50),
    intensidad_de_subvencion DECIMAL(5,2),
    intensidad_de_prestamo DECIMAL(5,2),
    tipo_financiacion VARCHAR(255),
    forma_y_plazo_de_cobro TEXT,
    minimis VARCHAR(255),
    region_de_aplicacion VARCHAR(255),
    tipo_de_consorcio VARCHAR(255),
    costes_elegibles TEXT,
    dotacion_presupuestaria DECIMAL(15,2),
    numero_potencial_de_ayudas INTEGER,
    tasa_de_exito DECIMAL(5,2),
    link_ficha_tecnica TEXT,
    link_orden_de_bases TEXT,
    link_convocatoria TEXT,
    link_plantilla_memoria TEXT,
    criterios_valoracion TEXT,
    documentacion_solicitud TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creem la taula per als embeddings (només si no existeix)
CREATE TABLE IF NOT EXISTS documentos (
  id SERIAL PRIMARY KEY,
  convocatoria_id INTEGER REFERENCES convocatorias(id) ON DELETE CASCADE,
  fuente TEXT NOT NULL, -- Ex: "web", "pdf"
  url TEXT,
  titulo TEXT, -- opcional: pot ser l’h1 o títol del document
  texto TEXT,  -- text complet del document (opcional)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);