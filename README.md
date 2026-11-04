# Aula de Clases SI2

Repositorio base para el trabajo universitario de Ingeniería Informática (UMSS). Contiene únicamente la arquitectura inicial: no incluye funcionalidades, lógica de negocio, rutas, interfaz implementada ni pruebas.

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

Consultar [la documentación de arquitectura](docs/arquitectura.md) antes de agregar código.
