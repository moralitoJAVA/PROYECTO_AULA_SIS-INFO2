# Proyecto Aula SIS-INFO2

Base de trabajo para Ingeniería Informática de la UMSS, orientada a prácticas de Extreme Programming (XP): Historias de Usuario (HU), tarjetas CRC, TDD y Pair Programming.

## Tecnologías

- HTML5
- CSS3
- JavaScript puro con módulos ES
- Python 3 estándar como servidor y API
- SQLite como base de datos SQL local

No usa frameworks, librerías externas, npm ni bundlers.

## Estructura

```text
front/
├── index.html              Página principal y menú de HU
├── css/styles.css          Estilos globales responsive
└── js/
    ├── app.js              Punto de entrada de la interfaz
    ├── core/api.js          Cliente para la API Python
    └── hus/README.md       Espacio para módulos por HU
back/
├── servidor.py             Servidor HTTP y API con Python estándar
├── esquema.sql             Esquema inicial de SQLite
└── datos.db                Base SQLite (se genera al iniciar)
```

## Ejecución

Se requiere Python 3. Desde la raíz del proyecto ejecutar:

```bash
python3 back/servidor.py
```

Después abrir `http://localhost:8000` en el navegador. El servidor crea automáticamente `back/datos.db` a partir de `back/esquema.sql` en el primer inicio.

## Convención para las HU

Cada HU debe tener un módulo dentro de `front/js/hus/`, por ejemplo `hu-01.js`. Desde `front/js/app.js` se registra en el menú y se conecta a su vista. Las operaciones que persistan datos deben consumir rutas de la API bajo `/api/`. Mantener criterios de aceptación, tarjetas CRC y evidencia de pruebas junto al código o en la documentación de cada HU.

## Equipo

Completar nombres, roles y responsabilidades del equipo antes de la entrega.
