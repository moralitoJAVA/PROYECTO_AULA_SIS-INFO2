# Aula de Clases SI2

Repositorio del trabajo universitario de Ingeniería Informática (UMSS), con módulos de asistencia, tareas, apuntes y nota final.

## Arquitectura

El proyecto se organiza en capas para separar responsabilidades:

```text
src/
├── api/           Punto de entrada, rutas y adaptadores HTTP
├── modelo/        Entidades y reglas del dominio
├── repositorio/   Persistencia y contratos de acceso a datos
└── servicio/      Casos de uso y coordinación de reglas de negocio
web/
├── css/           Estilos de la interfaz
└── js/            Comportamiento de la interfaz
tests/             Pruebas automatizadas, con estructura paralela a src/
docs/              Diagramas, decisiones y documentación técnica
```

## Reglas de organización

- La capa `web` no accede directamente a `modelo` ni a `repositorio`; se comunica mediante `api`.
- `api` delega los casos de uso en `servicio`.
- `servicio` aplica reglas de negocio usando `modelo` y contratos de `repositorio`.
- `repositorio` concentra el acceso a la fuente de datos y no contiene reglas de negocio.
- Cada módulo nuevo debe tener sus pruebas correspondientes en `tests/`.

Consultar [la documentación de arquitectura](docs/arquitectura.md) y el [diagrama de clases](docs/diagrama-clases.md) antes de agregar código.

## Cómo levantar el proyecto

Se necesita Python 3. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app 'src.api.app:crear_app()' run --debug
```

Abrir `http://127.0.0.1:5000` en el navegador. La aplicación crea y usa el archivo local `aula_virtual.db`.

Para ejecutar las pruebas:

```bash
pytest -q
```

### Estado actual de integración

La HU-01 de asistencia pasó sus 49 pruebas antes de integrarse. Actualmente la suite completa no inicia porque código ya integrado de HU-02/HU-04 contiene errores de indentación en `src/modelo/calculadora_nota_final.py`, `tests/test_calculadora_nota_final.py` y `tests/test_porcentaje.py`. Corregir esos archivos es necesario antes de levantar la aplicación completa o ejecutar toda la suite.
