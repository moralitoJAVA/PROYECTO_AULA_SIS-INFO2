-- Esquema de referencia SQLite. La aplicación usa localStorage en el navegador.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pregunta_clase (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  texto TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participacion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pregunta_id INTEGER NOT NULL,
  fecha TEXT NOT NULL,
  es_correcta INTEGER NOT NULL CHECK (es_correcta IN (0, 1)),
  FOREIGN KEY (pregunta_id) REFERENCES pregunta_clase(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_participacion_pregunta_id ON participacion(pregunta_id);

CREATE TABLE IF NOT EXISTS tarea (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  numero INTEGER NOT NULL UNIQUE,
  tema TEXT NOT NULL,
  hora_limite TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entrega (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tarea_id INTEGER NOT NULL,
  fecha_entrega TEXT NOT NULL,
  a_tiempo INTEGER NOT NULL CHECK (a_tiempo IN (0, 1)),
  FOREIGN KEY (tarea_id) REFERENCES tarea(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_entrega_tarea_id ON entrega(tarea_id);

CREATE TABLE IF NOT EXISTS lectura (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  nombre_archivo TEXT NOT NULL,
  contenido_pdf TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS apunte (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lectura_id INTEGER,
  fecha_clase TEXT NOT NULL,
  contenido TEXT NOT NULL,
  creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lectura_id) REFERENCES lectura(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_apunte_lectura_id ON apunte(lectura_id);

CREATE TABLE IF NOT EXISTS penalizacion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dia_clase TEXT NOT NULL CHECK (dia_clase IN ('martes', 'miercoles', 'viernes')),
  fecha_llegada TEXT NOT NULL,
  fecha_siguiente_clase TEXT NOT NULL,
  estado TEXT NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Cumplida'))
);
