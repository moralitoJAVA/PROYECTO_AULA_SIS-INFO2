-- Datos de ejemplo equivalentes a BaseDatos.poblarEjemplo().
INSERT INTO pregunta_clase (id, texto) VALUES
  (1, '¿Qué representa una tarjeta CRC?'),
  (2, '¿Cuál es el primer paso de TDD?'),
  (3, '¿Qué rol apoya al conductor en Pair Programming?'),
  (4, '¿Cómo se redacta una Historia de Usuario?'),
  (5, '¿Qué significa integración continua?');

INSERT INTO tarea (id, numero, tema, hora_limite) VALUES
  (1, 1, 'Tarjetas CRC', '2026-11-10T23:59:00'),
  (2, 2, 'Pruebas TDD', '2026-11-17T23:59:00');

INSERT INTO lectura (id, titulo, nombre_archivo, contenido_pdf) VALUES
  (1, 'Introducción a XP', 'introduccion-xp.pdf', 'data:application/pdf;base64,RG9jdW1lbnRvIGRlIHBydWViYQ=='),
  (2, 'Guía de TDD', 'guia-tdd.pdf', 'data:application/pdf;base64,R3TDrWEgZGUgVEREIGRlIHBydWViYQ==');

INSERT INTO apunte (id, lectura_id, fecha_clase, contenido, creado_en, actualizado_en) VALUES
  (1, 1, '2026-11-03', 'XP prioriza retroalimentación frecuente.', '2026-11-03T08:00:00', '2026-11-03T08:00:00'),
  (2, 2, '2026-11-05', 'TDD sigue el ciclo rojo, verde y refactorización.', '2026-11-05T08:00:00', '2026-11-05T08:00:00'),
  (3, NULL, '2026-11-07', 'Definir criterios de aceptación antes de programar.', '2026-11-07T08:00:00', '2026-11-07T08:00:00');

INSERT INTO penalizacion (id, dia_clase, fecha_llegada, fecha_siguiente_clase, estado) VALUES
  (1, 'martes', '2026-11-03T08:15:00', '2026-11-04', 'Pendiente'),
  (2, 'miercoles', '2026-11-04T08:10:00', '2026-11-06', 'Cumplida'),
  (3, 'viernes', '2026-11-06T08:20:00', '2026-11-10', 'Pendiente');
