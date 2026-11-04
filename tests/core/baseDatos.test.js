import { BaseDatos, TareaRepositorio } from "../../js/core/baseDatos.js";

class AlmacenamientoSimulado {
  constructor() { this.datos = new Map(); }
  get length() { return this.datos.size; }
  key(indice) { return [...this.datos.keys()][indice] ?? null; }
  getItem(clave) { return this.datos.has(clave) ? this.datos.get(clave) : null; }
  setItem(clave, valor) { this.datos.set(clave, String(valor)); }
  removeItem(clave) { this.datos.delete(clave); }
}

function afirmar(condicion, mensaje) { if (!condicion) throw new Error(mensaje); }
function afirmarIgual(actual, esperado, mensaje) { afirmar(actual === esperado, `${mensaje}. Esperado: ${esperado}; recibido: ${actual}`); }
function afirmarError(accion, texto) {
  try { accion(); } catch (error) { afirmar(error.message.includes(texto), `El error debe incluir '${texto}'`); return; }
  throw new Error("Se esperaba que la acción lanzara un error.");
}
function crearBase() { return new BaseDatos(new AlmacenamientoSimulado()); }

const CASOS = [
  ["inserta y obtiene un registro", () => {
    const base = crearBase();
    const pregunta = base.insertar("pregunta_clase", { texto: "¿Qué es XP?" });
    afirmarIgual(base.obtenerPorId("pregunta_clase", pregunta.id).texto, "¿Qué es XP?", "Debe recuperar la pregunta");
  }],
  ["asigna ids autoincrementales", () => {
    const base = crearBase();
    afirmarIgual(base.insertar("pregunta_clase", { texto: "A" }).id, 1, "El primer id debe ser 1");
    afirmarIgual(base.insertar("pregunta_clase", { texto: "B" }).id, 2, "El segundo id debe ser 2");
  }],
  ["rechaza una clave foránea inválida", () => {
    afirmarError(() => crearBase().insertar("participacion", { pregunta_id: 99, fecha: "2026-11-03", es_correcta: 1 }), "pregunta_id 99 no existe");
  }],
  ["rechaza valores CHECK inválidos", () => {
    afirmarError(() => crearBase().insertar("penalizacion", { dia_clase: "lunes", fecha_llegada: "2026-11-03", fecha_siguiente_clase: "2026-11-04" }), "dia_clase");
  }],
  ["rechaza números de tarea duplicados", () => {
    const tareas = new TareaRepositorio(crearBase());
    tareas.crear({ numero: 1, tema: "CRC", hora_limite: "23:59" });
    afirmarError(() => tareas.crear({ numero: 1, tema: "TDD", hora_limite: "23:59" }), "número de tarea 1");
  }],
  ["actualiza un registro", () => {
    const base = crearBase();
    const tarea = base.insertar("tarea", { numero: 1, tema: "CRC", hora_limite: "23:59" });
    afirmarIgual(base.actualizar("tarea", tarea.id, { tema: "TDD" }).tema, "TDD", "Debe guardar el cambio");
  }],
  ["elimina un registro", () => {
    const base = crearBase();
    const pregunta = base.insertar("pregunta_clase", { texto: "A" });
    afirmarIgual(base.eliminar("pregunta_clase", pregunta.id), true, "Debe indicar eliminación");
    afirmarIgual(base.obtenerPorId("pregunta_clase", pregunta.id), null, "No debe encontrar el registro");
  }],
  ["reinicia solo las claves del proyecto", () => {
    const almacenamiento = new AlmacenamientoSimulado();
    almacenamiento.setItem("ajeno", "conservar");
    const base = new BaseDatos(almacenamiento);
    base.insertar("pregunta_clase", { texto: "A" });
    base.reiniciar();
    afirmarIgual(almacenamiento.getItem("ajeno"), "conservar", "No debe borrar claves ajenas");
    afirmarIgual(base.obtenerTodos("pregunta_clase").length, 0, "Debe borrar los datos del proyecto");
  }],
  ["puebla los datos de ejemplo", () => {
    const base = crearBase();
    base.poblarEjemplo();
    afirmarIgual(base.obtenerTodos("pregunta_clase").length, 5, "Debe crear cinco preguntas");
    afirmarIgual(base.obtenerTodos("tarea").length, 2, "Debe crear dos tareas");
    afirmarIgual(base.obtenerTodos("penalizacion").length, 3, "Debe crear tres penalizaciones");
  }],
];

export function ejecutarPruebas() {
  return CASOS.map(([nombre, prueba]) => {
    try { prueba(); return { nombre, error: null }; } catch (error) { return { nombre, error }; }
  });
}
