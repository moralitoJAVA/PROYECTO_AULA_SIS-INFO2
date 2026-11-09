/* VistaControlLectura: lectura, preguntas, estado y botón "Enviar respuestas". */
const CLAVE_NOMBRE = "control_lectura_nombre";
let estudiante = "";

const vistaLista = document.getElementById("lista-vista");
const vistaDetalle = document.getElementById("detalle-vista");

function leerNombreGuardado() {
  try { return localStorage.getItem(CLAVE_NOMBRE) || ""; } catch (error) { return ""; }
}

function guardarNombre(nombre) {
  try { localStorage.setItem(CLAVE_NOMBRE, nombre); } catch (error) { /* sin almacenamiento: no pasa nada */ }
}

function pintarNota(control) {
  if (!control.calificacion_publicada) return "";
  return `<div class="calificacion"><div>Calificación: <strong>${escapar(control.nota)}</strong> / ${escapar(control.puntaje_maximo)}</div>` +
    `<div>${control.retroalimentacion ? "Retroalimentación: " + escapar(control.retroalimentacion) : "Sin retroalimentación escrita."}</div></div>`;
}

function pintarLista(controles) {
  document.getElementById("lista-vacia").hidden = controles.length > 0;
  document.getElementById("lista").innerHTML = controles.map((c) => {
    const accion = c.puede_responder ? "Responder" : "Ver";
    return `<li class="control-item"><div><h3>${escapar(c.titulo)}</h3>` +
      `<p>Lectura: ${escapar(c.lectura.titulo)} — ${escapar(c.lectura.autor)}</p>` +
      `<p>Abre: ${escapar(fechaHoraLegible(c.apertura))} · Cierra: ${escapar(fechaHoraLegible(c.cierre))}</p>` +
      `<div class="etiquetas">${etiquetaDe(c.estado)}${c.puntualidad ? etiquetaDe(c.puntualidad) : ""}${etiquetaDe(c.ventana)}` +
      `${c.calificacion_publicada ? '<span class="etiqueta info">Calificado</span>' : ""}</div></div>` +
      `<button class="boton ${c.puede_responder ? "primario" : "secundario"}" type="button" data-id="${c.id}">${accion}</button></li>`;
  }).join("");
}

async function cargarLista() {
  const controles = await llamarApi(`/api/controles-lectura?estudiante=${encodeURIComponent(estudiante)}`);
  pintarLista(controles);
  vistaDetalle.hidden = true;
  vistaLista.hidden = false;
}

function motivoBloqueo(control) {
  if (control.estado === "Respondido" && !control.puede_responder) return "Ya enviaste este control. Solo el docente puede habilitar otro intento.";
  if (control.ventana === "Aún no abre") return `El control abre el ${fechaHoraLegible(control.apertura)}.`;
  return `El control cerró el ${fechaHoraLegible(control.cierre)}. Ya no puedes responder.`;
}

function pintarPreguntas(control) {
  const editable = control.puede_responder;
  return control.preguntas.map((p, i) =>
    `<div class="pregunta" data-obligatoria="${p.obligatoria}">` +
    `<label for="respuesta-${i}">${i + 1}. ${escapar(p.enunciado)} ${p.obligatoria ? '<span class="obligatoria" title="Obligatoria">*</span>' : '<span class="ayuda">(opcional)</span>'}</label>` +
    `<textarea id="respuesta-${i}" rows="4" ${editable ? "" : "disabled"}>${escapar((control.respuestas && control.respuestas[i]) || "")}</textarea></div>`
  ).join("");
}

function pintarDetalle(control, confirmacion = "") {
  const respondido = control.estado === "Respondido";
  const estado = `<div class="etiquetas">${etiquetaDe(control.estado)}${control.puntualidad ? etiquetaDe(control.puntualidad) : ""}${etiquetaDe(control.ventana)}</div>`;
  document.getElementById("detalle").innerHTML =
    `<div class="tarjeta"><h2>${escapar(control.titulo)}</h2>${estado}` +
    `<p class="ayuda">Abre: ${escapar(fechaHoraLegible(control.apertura))} · Cierra: ${escapar(fechaHoraLegible(control.cierre))}` +
    `${respondido ? ` · Enviado: ${escapar(fechaHoraLegible(control.fecha_hora_envio))}` : ""}</p></div>` +
    `<div class="tarjeta"><h2>Lectura asignada</h2><p class="ayuda">Léela antes de responder.</p>` +
    `<div class="lectura-caja"><strong>${escapar(control.lectura.titulo)}</strong><span>${escapar(control.lectura.autor)}</span>` +
    `<span>${enlaceDeLectura(control.lectura)}</span></div></div>` +
    `<form id="formulario" class="tarjeta" novalidate><h2>Preguntas</h2>` +
    (confirmacion ? `<p class="confirmacion" role="status">${escapar(confirmacion)}. Estado: Respondido.</p>` : "") +
    pintarNota(control) +
    (control.puede_responder ? '<p class="ayuda">Las preguntas con <span class="obligatoria" style="color:var(--urgente)">*</span> son obligatorias.</p>'
      : (confirmacion ? "" : `<div class="advertencia" role="status"><p>${escapar(motivoBloqueo(control))}</p></div>`)) +
    pintarPreguntas(control) +
    (control.puede_responder ? '<button class="boton primario grande" type="submit">Enviar respuestas</button>' : "") +
    `</form>`;
  if (control.puede_responder) document.getElementById("formulario").addEventListener("submit", (e) => enviar(e, control));
  vistaLista.hidden = true;
  vistaDetalle.hidden = false;
}

async function abrirControl(id) {
  const control = await llamarApi(`/api/controles-lectura/${id}?estudiante=${encodeURIComponent(estudiante)}`);
  pintarDetalle(control);
}

async function enviar(evento, control) {
  evento.preventDefault();
  const bloques = [...document.querySelectorAll(".pregunta")];
  const respuestas = bloques.map((bloque) => bloque.querySelector("textarea").value);
  bloques.forEach((bloque, i) => bloque.classList.toggle("falta", bloque.dataset.obligatoria === "true" && !respuestas[i].trim()));
  const falta = bloques.findIndex((bloque) => bloque.classList.contains("falta"));
  if (falta >= 0) {
    mostrarMensaje("mensaje", `Falta responder la pregunta obligatoria ${falta + 1}`, "error");
    bloques[falta].querySelector("textarea").focus();
    return;
  }
  const boton = evento.submitter;
  if (boton) boton.disabled = true;
  try {
    const resultado = await llamarApi(`/api/controles-lectura/${control.id}/respuestas`, {
      method: "POST", body: JSON.stringify({ estudiante, respuestas }),
    });
    const actualizado = await llamarApi(`/api/controles-lectura/${control.id}?estudiante=${encodeURIComponent(estudiante)}`);
    pintarDetalle(actualizado, resultado.mensaje);
    mostrarMensaje("mensaje", resultado.mensaje);
  } catch (error) {
    if (boton) boton.disabled = false;
    mostrarMensaje("mensaje", error.message || "No se pudo enviar el control. Inténtalo de nuevo.", "error");
  }
}

async function identificarse(nombre) {
  const registrado = await llamarApi("/api/controles-lectura/estudiantes", { method: "POST", body: JSON.stringify({ nombre }) });
  estudiante = registrado.nombre;
  guardarNombre(estudiante);
  document.getElementById("nombre").value = estudiante;
  await cargarLista();
}

document.getElementById("identidad").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try { await identificarse(document.getElementById("nombre").value); }
  catch (error) { mostrarMensaje("mensaje", error.message, "error"); }
});

document.getElementById("lista").addEventListener("click", (evento) => {
  const boton = evento.target.closest("button[data-id]");
  if (boton) abrirControl(boton.dataset.id).catch((error) => mostrarMensaje("mensaje", error.message, "error"));
});

document.getElementById("volver").addEventListener("click", () => cargarLista().catch((e) => mostrarMensaje("mensaje", e.message, "error")));

const nombreGuardado = leerNombreGuardado();
if (nombreGuardado) identificarse(nombreGuardado).catch(() => {});