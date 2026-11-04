-- Esquema inicial de la base de datos del proyecto.
-- Cada HU puede añadir sus tablas mediante scripts SQL versionados.

CREATE TABLE IF NOT EXISTS historias_usuario (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  titulo TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  estado TEXT NOT NULL DEFAULT 'pendiente',
  creada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
