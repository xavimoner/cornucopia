-- init_db.sql
-- Creem la taula per emmagatzemar dades estructurades (SQL)

CREATE TABLE IF NOT EXISTS proyectos (
    id SERIAL PRIMARY KEY,
    organismo VARCHAR(255),
    nombre VARCHAR(255),
    linea VARCHAR(255),
    fecha_inicio DATE,
    fecha_fin DATE,
    anio INTEGER,
    area VARCHAR(255),
    presupuesto_minimo VARCHAR(255),
    presupuesto_maximo VARCHAR(255),
    duracion_minima VARCHAR(255),
    duracion_maxima VARCHAR(255),
    tipo_financiacion VARCHAR(255),
    forma_y_plazo_de_cobro VARCHAR(255),
    minimis VARCHAR(255)
);

-- Creem la taula per emmagatzemar camps vectorials

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS proyectos_vector (
    id SERIAL PRIMARY KEY,
    proyecto_id INTEGER REFERENCES proyectos(id),
    objetivo_vector vector(1536),  -- Ajusta la mida del vector segons el model utilitzat
    beneficiarios_vector vector(1536),
    costes_elegibles_vector vector(1536),
    criterios_valoracion_vector vector(1536)
);
