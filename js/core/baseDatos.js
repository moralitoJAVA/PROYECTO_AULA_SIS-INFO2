const PREFIJO = "sis2_";
const TABLAS = ["pregunta_clase", "participacion", "tarea", "entrega", "lectura", "apunte", "penalizacion"];
const LIMITE_PDF_BYTES = 2 * 1024 * 1024;

const DATOS_EJEMPLO = {
  pregunta_clase: [
    { id: 1, texto: "¿Qué representa una tarjeta CRC?" },
    { id: 2, texto: "¿Cuál es el primer paso de TDD?" },
    { id: 3, texto: "¿Qué rol apoya al conductor en Pair Programming?" },
    { id: 4, texto: "¿Cómo se redacta una Historia de Usuario?" },
    { id: 5, texto: "¿Qué significa integración continua?" },
  ],
  tarea: [
    { id: 1, numero: 1, tema: "Tarjetas CRC", hora_limite: "2026-11-10T23:59:00" },
    { id: 2, numero: 2, tema: "Pruebas TDD", hora_limite: "2026-11-17T23:59:00" },
  ],
  lectura: [
    { id: 1, titulo: "Introducción a XP", nombre_archivo: "introduccion-xp.pdf", contenido_pdf: "data:application/pdf;base64,RG9jdW1lbnRvIGRlIHBydWViYQ==" },
    { id: 2, titulo: "Guía de TDD", nombre_archivo: "guia-tdd.pdf", contenido_pdf: "data:application/pdf;base64,R3TDrWEgZGUgVEREIGRlIHBydWViYQ==" },
  ],
  apunte: [
    { id: 1, lectura_id: 1, fecha_clase: "2026-11-03", contenido: "XP prioriza retroalimentación frecuente.", creado_en: "2026-11-03T08:00:00", actualizado_en: "2026-11-03T08:00:00" },
    { id: 2, lectura_id: 2, fecha_clase: "2026-11-05", contenido: "TDD sigue el ciclo rojo, verde y refactorización.", creado_en: "2026-11-05T08:00:00", actualizado_en: "2026-11-05T08:00:00" },
    { id: 3, lectura_id: null, fecha_clase: "2026-11-07", contenido: "Definir criterios de aceptación antes de programar.", creado_en: "2026-11-07T08:00:00", actualizado_en: "2026-11-07T08:00:00" },
  ],
  penalizacion: [
    { id: 1, dia_clase: "martes", fecha_llegada: "2026-11-03T08:15:00", fecha_siguiente_clase: "2026-11-04", estado: "Pendiente" },
    { id: 2, dia_clase: "miercoles", fecha_llegada: "2026-11-04T08:10:00", fecha_siguiente_clase: "2026-11-06", estado: "Cumplida" },
    { id: 3, dia_clase: "viernes", fecha_llegada: "2026-11-06T08:20:00", fecha_siguiente_clase: "2026-11-10", estado: "Pendiente" },
  ],
};

/** Capa de persistencia local que simula tablas SQL mediante localStorage. */
export class BaseDatos {
  constructor(almacenamiento = globalThis.localStorage) {
    if (!almacenamiento) throw new Error("localStorage no está disponible en este navegador.");
    this.almacenamiento = almacenamiento;
  }

  insertar(tabla, registro) {
    return this.#ejecutar("insertar", () => {
      this.#validarTabla(tabla);
      const registros = this.#leerTabla(tabla);
      const nuevo = { ...registro, id: this.#proximoId(tabla) };
      this.#validarRegistro(tabla, nuevo, registros);
      if (tabla === "apunte") {
        const ahora = new Date().toISOString();
        nuevo.creado_en ??= ahora;
        nuevo.actualizado_en ??= ahora;
      }
      registros.push(nuevo);
      this.#guardarTabla(tabla, registros);
      this.#guardarIdActual(tabla, nuevo.id);
      return { ...nuevo };
    });
  }

  obtenerTodos(tabla) {
    return this.#ejecutar("leer", () => this.#leerTabla(tabla).map((registro) => ({ ...registro })));
  }

  obtenerPorId(tabla, id) {
    return this.#ejecutar("leer", () => {
      const encontrado = this.#leerTabla(tabla).find((registro) => registro.id === Number(id));
      return encontrado ? { ...encontrado } : null;
    });
  }

  actualizar(tabla, id, cambios) {
    return this.#ejecutar("actualizar", () => {
      this.#validarTabla(tabla);
      const registros = this.#leerTabla(tabla);
      const indice = registros.findIndex((registro) => registro.id === Number(id));
      if (indice === -1) throw new Error(`No existe un registro con id ${id} en ${tabla}.`);
      const actualizado = { ...registros[indice], ...cambios, id: registros[indice].id };
      if (tabla === "apunte") actualizado.actualizado_en = new Date().toISOString();
      this.#validarRegistro(tabla, actualizado, registros.filter((_, i) => i !== indice));
      registros[indice] = actualizado;
      this.#guardarTabla(tabla, registros);
      return { ...actualizado };
    });
  }

  eliminar(tabla, id) {
    return this.#ejecutar("eliminar", () => {
      this.#validarTabla(tabla);
      const registros = this.#leerTabla(tabla);
      const existe = registros.some((registro) => registro.id === Number(id));
      if (!existe) return false;
      this.#guardarTabla(tabla, registros.filter((registro) => registro.id !== Number(id)));
      this.#aplicarBorradoReferencial(tabla, Number(id));
      return true;
    });
  }

  buscar(tabla, filtroFn) {
    if (typeof filtroFn !== "function") throw new Error("El filtro de búsqueda debe ser una función.");
    return this.obtenerTodos(tabla).filter(filtroFn);
  }

  reiniciar() {
    return this.#ejecutar("reiniciar", () => {
      const claves = [];
      for (let indice = 0; indice < this.almacenamiento.length; indice += 1) {
        const clave = this.almacenamiento.key(indice);
        if (clave?.startsWith(PREFIJO)) claves.push(clave);
      }
      claves.forEach((clave) => this.almacenamiento.removeItem(clave));
    });
  }

  poblarEjemplo() {
    this.reiniciar();
    Object.entries(DATOS_EJEMPLO).forEach(([tabla, registros]) => {
      registros.forEach(({ id: _id, ...registro }) => this.insertar(tabla, registro));
    });
  }

  #ejecutar(operacion, accion) {
    try {
      return accion();
    } catch (error) {
      if (error instanceof Error && !/localStorage|JSON|almacenamiento/.test(error.message)) throw error;
      throw new Error(`No se pudo ${operacion} en localStorage. Verifique que no esté bloqueado ni lleno. Detalle: ${error.message}`);
    }
  }

  #clave(tabla) { return `${PREFIJO}${tabla}`; }
  #claveContador(tabla) { return `${PREFIJO}contador_${tabla}`; }

  #leerTabla(tabla) {
    this.#validarTabla(tabla);
    const contenido = this.almacenamiento.getItem(this.#clave(tabla));
    if (contenido === null) return [];
    const datos = JSON.parse(contenido);
    if (!Array.isArray(datos)) throw new Error(`La tabla local ${tabla} tiene un formato inválido.`);
    return datos;
  }

  #guardarTabla(tabla, registros) {
    this.almacenamiento.setItem(this.#clave(tabla), JSON.stringify(registros));
  }

  #proximoId(tabla) {
    const clave = this.#claveContador(tabla);
    return Number(this.almacenamiento.getItem(clave) || 0) + 1;
  }

  #guardarIdActual(tabla, id) { this.almacenamiento.setItem(this.#claveContador(tabla), String(id)); }

  #validarTabla(tabla) {
    if (!TABLAS.includes(tabla)) throw new Error(`La tabla '${tabla}' no existe en la base de datos.`);
  }

  #existe(tabla, id) { return this.#leerTabla(tabla).some((registro) => registro.id === Number(id)); }

  #validarRegistro(tabla, registro, otrosRegistros) {
    if (tabla === "participacion" && !this.#existe("pregunta_clase", registro.pregunta_id)) {
      throw new Error(`La pregunta_id ${registro.pregunta_id} no existe en pregunta_clase.`);
    }
    if (tabla === "entrega" && !this.#existe("tarea", registro.tarea_id)) {
      throw new Error(`La tarea_id ${registro.tarea_id} no existe en tarea.`);
    }
    if (tabla === "apunte" && registro.lectura_id !== null && registro.lectura_id !== undefined && !this.#existe("lectura", registro.lectura_id)) {
      throw new Error(`La lectura_id ${registro.lectura_id} no existe en lectura.`);
    }
    if (tabla === "participacion" && ![0, 1].includes(Number(registro.es_correcta))) throw new Error("es_correcta debe ser 0 o 1.");
    if (tabla === "entrega" && ![0, 1].includes(Number(registro.a_tiempo))) throw new Error("a_tiempo debe ser 0 o 1.");
    if (tabla === "penalizacion") {
      if (!["martes", "miercoles", "viernes"].includes(registro.dia_clase)) throw new Error("dia_clase debe ser martes, miercoles o viernes.");
      if (!(["Pendiente", "Cumplida"].includes(registro.estado ?? "Pendiente"))) throw new Error("estado debe ser Pendiente o Cumplida.");
      registro.estado ??= "Pendiente";
    }
    if (tabla === "tarea" && otrosRegistros.some((tarea) => Number(tarea.numero) === Number(registro.numero))) {
      throw new Error(`El número de tarea ${registro.numero} ya está registrado.`);
    }
    if (tabla === "lectura") this.#validarPdf(registro.contenido_pdf);
  }

  #validarPdf(contenidoPdf) {
    if (typeof contenidoPdf !== "string" || !contenidoPdf.startsWith("data:")) throw new Error("contenido_pdf debe ser un archivo PDF en formato data URL.");
    const carga = contenidoPdf.split(",")[1] || "";
    const bytes = Math.floor((carga.length * 3) / 4) - (carga.endsWith("==") ? 2 : carga.endsWith("=") ? 1 : 0);
    if (bytes > LIMITE_PDF_BYTES) throw new Error("El PDF supera el límite permitido de 2 MB.");
  }

  #aplicarBorradoReferencial(tabla, id) {
    if (tabla === "pregunta_clase") this.#guardarTabla("participacion", this.#leerTabla("participacion").filter((registro) => registro.pregunta_id !== id));
    if (tabla === "tarea") this.#guardarTabla("entrega", this.#leerTabla("entrega").filter((registro) => registro.tarea_id !== id));
    if (tabla === "lectura") this.#guardarTabla("apunte", this.#leerTabla("apunte").map((registro) => registro.lectura_id === id ? { ...registro, lectura_id: null } : registro));
  }
}

class RepositorioBase {
  constructor(baseDatos, tabla) { this.baseDatos = baseDatos; this.tabla = tabla; }
  crear(registro) { return this.baseDatos.insertar(this.tabla, registro); }
  listar() { return this.baseDatos.obtenerTodos(this.tabla); }
  buscarPorId(id) { return this.baseDatos.obtenerPorId(this.tabla, id); }
  actualizar(id, cambios) { return this.baseDatos.actualizar(this.tabla, id, cambios); }
  eliminar(id) { return this.baseDatos.eliminar(this.tabla, id); }
  buscar(filtroFn) { return this.baseDatos.buscar(this.tabla, filtroFn); }
}

export class PreguntaClaseRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "pregunta_clase"); } }
export class ParticipacionRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "participacion"); } }
export class TareaRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "tarea"); } }
export class EntregaRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "entrega"); } }
export class LecturaRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "lectura"); } }
export class ApunteRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "apunte"); } }
export class PenalizacionRepositorio extends RepositorioBase { constructor(baseDatos) { super(baseDatos, "penalizacion"); } }
