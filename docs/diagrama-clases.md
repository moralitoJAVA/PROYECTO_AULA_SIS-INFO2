# Diagrama de clases

El siguiente diagrama representa las clases implementadas actualmente y sus dependencias principales. Las rutas HTTP se documentan en los módulos `api_*`; no son clases del dominio.

```mermaid
classDiagram
    class Estudiante {
        +nombre
        +obtenerDatos()
        +obtenerHistorial(registro)
        +obtenerDesglose(calculadora)
    }
    class Asistencia {
        -_registros
        +registrar(fecha, estado)
        +editar(fecha, estado)
        +existePara(fecha)
    }
    class Sesion {
        +materia
        +fecha
        +asistencia
        +esDiaDeClase()
        +listarAsistencia()
        +obtenerResumen()
    }
    class RegistroAsistencia {
        -_asistencia
        -_minimo
        +calcularPorcentaje()
        +hayAlerta()
        +obtenerHistorial()
    }
    class Tarea {
        +numero
        +titulo
        +fecha_limite
        +rubrica
        +registrar(ahora)
        +guardar(repositorio)
        +aDiccionario()
    }
    class TareaIndividual {
        +asignarATodos(estudiantes)
    }
    class TareaGrupal {
        +tamano_equipo
        +penalizacion
        +definirTamano(tamano)
        +definirPenalizacion(penalizacion)
    }
    class Entrega {
        +tarea
        +rubrica
        +estado
        +confirmar(ahora)
        +registrarCalificacion(nota, escala, comentarios)
        +estaPorVencer(ahora)
    }
    class Rubrica {
        -_criterios
        +agregarCriterio(nombre, puntaje)
        +obtenerPuntajeMaximo()
    }
    class Equipo {
        +integrantes
        +entrega
        +agregarIntegrante(nombre)
        +entregarPorGrupo(entrega, integrante, ahora)
        +repartirResultado(incumplen)
    }
    class Penalizacion {
        +calcularDescuento(incumplimientos)
        +guardarMotivo(repositorio, clave, incumplen)
    }
    class HistorialTareas {
        -_tareas
        -_entregas
        +listarPorEstado(estado)
        +obtenerNotas()
    }
    class GestorApuntes {
        -_repositorio
        +crear(vinculo, texto)
        +editar(clave, texto)
        +borrar(clave)
        +listarApuntes(vinculo)
    }
    class Porcentaje {
        -_pesos
        +obtenerPeso(componente)
        +validarSuma()
        +guardar(repositorio)
        +cargar(repositorio)$
    }
    class CalculadoraNotaFinal {
        -_porcentaje
        -_historial
        -_registro
        +calcular()
        +recalcular()
        +obtenerDesglose()
    }
    class GeneradorCodigo {
        -_ultimo
        +siguienteNumero()
        +generar(numero)
    }
    class Repositorio {
        <<abstract>>
        +guardar(clave, dato)*
        +obtener(clave)*
        +eliminar(clave)*
        +listar()*
    }
    class RepositorioMemoria {
        -_datos
    }
    class RepositorioSqlite {
        -_conexion
        -_tabla
    }
    class ServicioAsistencia {
        -_repositorio
        +registrarAsistencia(materia, fecha, estado)
        +editarAsistencia(materia, fecha, estado)
        +obtenerPorcentaje(materia)
    }
    class ServicioTareas {
        -_repo_tareas
        -_repo_entregas
        -_repo_equipos
        -_repo_penalizaciones
        +crearTarea(datos)
        +entregar(numero, archivos, enlaces, ahora)
        +entregarPorEquipo(...)
        +registrarCalificacion(...)
    }
    class Contexto {
        +conexion
        +repositorio(tabla)
    }

    Tarea <|-- TareaIndividual
    Tarea <|-- TareaGrupal
    Repositorio <|-- RepositorioMemoria
    Repositorio <|-- RepositorioSqlite
    Sesion *-- Asistencia
    RegistroAsistencia --> Asistencia
    Entrega --> Tarea
    Entrega --> Rubrica
    Tarea --> Rubrica
    Equipo --> Entrega
    Equipo --> Penalizacion
    HistorialTareas --> Tarea
    HistorialTareas --> Entrega
    CalculadoraNotaFinal --> Porcentaje
    CalculadoraNotaFinal --> HistorialTareas
    CalculadoraNotaFinal --> RegistroAsistencia
    Estudiante --> RegistroAsistencia
    Estudiante --> CalculadoraNotaFinal
    GestorApuntes --> Repositorio
    Penalizacion --> Repositorio
    ServicioAsistencia --> Repositorio
    ServicioAsistencia --> Sesion
    ServicioAsistencia --> RegistroAsistencia
    ServicioTareas --> Repositorio
    ServicioTareas --> Tarea
    ServicioTareas --> Entrega
    ServicioTareas --> Equipo
    ServicioTareas --> HistorialTareas
    Contexto --> RepositorioSqlite
```

## Capas y puntos de entrada

- `src/api/app.py` crea la aplicación Flask y carga los módulos `api_asistencia`, `api_tareas` y `api_nota_final`.
- `Contexto` entrega repositorios SQLite a las APIs y servicios.
- `ServicioAsistencia` implementa los casos de uso de HU-01.
- `ServicioTareas` implementa los casos de uso de tareas, entregas, equipos y apuntes.
- `CalculadoraNotaFinal` compone asistencia, tareas y pesos para calcular la nota final.
