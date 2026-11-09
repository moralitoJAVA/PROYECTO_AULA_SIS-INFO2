/* VistaRevisionDocente: lecturas, publicación de controles y revisión por estudiante. */
const listaPreguntas = document.getElementById("preguntas");
const selectControl = document.getElementById("revision-control");
let revisionActual = null;

function error(e) { mostrarMensaje("mensaje", e.message || "Ocurrió un error", "error"); }

// ---------- lecturas ----------
async function cargarLecturas() {
  const lecturas = await llamarApi("/api/lecturas");
  const select = document.getElementById("control-lectura");
  select.innerHTML = lecturas.length
    ? lecturas.map((l) => `<option value="${l.id}">${escapar(l.titulo)} — ${escapar(l.autor)}</option>`).join("")
    : '<option value="">Primero registra una lectura</option>';
}

document.getElementById("form-lectura").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    await llamarApi("/api/lecturas", { method: "POST", body: JSON.stringify({
      titulo: document.getElementById("lectura-titulo").value,
      autor: document.getElementById("lectura-autor").value,
      archivo: document.getElementById("lectura-archivo").value,
      enlace: document.getElementById("lectura-enlace").value,
    }) });
    evento.target.reset();
    await cargarLecturas();
    mostrarMensaje("mensaje", "Lectura registrada");
  } catch (e) { error(e); }
});

// ---------- control ----------
function agregarPregunta(enunciado = "", obligatoria = true) {
  const item = document.createElement("li");
  item.className = "pregunta-docente";
  item.innerHTML = `<input class="enunciado" required aria-label="Enunciado de la pregunta" placeholder="Escribe la pregunta" value="${escapar(enunciado)}">` +
    `<label class="casilla"><input class="obligatoria" type="checkbox" ${obligatoria ? "checked" : ""}> Obligatoria</label>` +
    '<button type="button" class="boton secundario quitar-criterio" aria-label="Quitar pregunta">Quitar</button>';
  item.querySelector("button").addEventListener("click", () => item.remove());
  listaPreguntas.append(item);
}

document.getElementById("agregar-pregunta").addEventListener("click", () => agregarPregunta());

document.getElementById("form-control").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    const lectura = document.getElementById("control-lectura").value;
    await llamarApi("/api/controles-lectura", { method: "POST", body: JSON.stringify({
      titulo: document.getElementById("control-titulo").value,
      id_lectura: lectura ? Number(lectura) : null,
      apertura: document.getElementById("control-apertura").value,
      cierre: document.getElementById("control-cierre").value,
      puntaje_maximo: document.getElementById("control-puntaje").value,
      preguntas: [...listaPreguntas.children].map((item) => ({
        enunciado: item.querySelector(".enunciado").value,
        obligatoria: item.querySelector(".obligatoria").checked,
      })),
    }) });
    evento.target.reset();
    listaPreguntas.replaceChildren();
    agregarPregunta();
    mostrarMensaje("mensaje", "Control publicado");
    await cargarControles(true);
  } catch (e) { error(e); }
});

// ---------- revisión ----------
async function cargarControles(seleccionarUltimo = false) {
  const controles = await llamarApi("/api/controles-lectura");
  selectControl.innerHTML = controles.length
    ? controles.map((c) => `<option value="${c.id}">${escapar(c.titulo)}</option>`).join("")
    : '<option value="">Aún no hay controles publicados</option>';
  if (controles.length && seleccionarUltimo) selectControl.value = String(Math.max(...controles.map((c) => c.id)));
  await cargarRevision();
}

async function cargarRevision() {
  document.getElementById("revision-detalle").hidden = true;
  const id = selectControl.value;
  const filas = document.getElementById("revision-filas");
  if (!id) { revisionActual = null; filas.innerHTML = ""; document.getElementById("tabla-caja").hidden = true; document.getElementById("revision-vacia").hidden = true; return; }
  revisionActual = await llamarApi(`/api/controles-lectura/${id}/revision`);
  const lista = revisionActual.estudiantes;
  document.getElementById("revision-vacia").hidden = lista.length > 0;
  document.getElementById("tabla-caja").hidden = lista.length === 0;
  filas.innerHTML = lista.map((e, i) =>
    `<tr><td>${escapar(e.estudiante)}</td><td>${etiquetaDe(e.estado_revision)}${e.intento_habilitado ? ' <span class="etiqueta info">Nuevo intento habilitado</span>' : ""}</td>` +
    `<td>${e.fecha_hora_envio ? escapar(fechaHoraLegible(e.fecha_hora_envio)) : "—"}</td>` +
    `<td class="num">${e.nota === null ? "—" : escapar(e.nota)}${e.nota !== null && e.calificacion_publicada ? " ✓" : ""}</td>` +
    `<td><div class="fila-acciones"><button class="boton secundario chico" type="button" data-accion="revisar" data-i="${i}" ${e.fecha_hora_envio ? "" : "disabled"}>Revisar</button>` +
    `<button class="boton secundario chico" type="button" data-accion="intento" data-i="${i}">Habilitar nuevo intento</button></div></td></tr>`
  ).join("");
}

function pintarRevisionDetalle(indice) {
  const e = revisionActual.estudiantes[indice];
  const { control, lectura, preguntas } = revisionActual;
  const caja = document.getElementById("revision-detalle");
  caja.innerHTML = `<h2>${escapar(e.estudiante)} — ${escapar(control.titulo)}</h2>` +
    `<div class="etiquetas">${etiquetaDe(e.estado_revision)}${e.puntualidad ? etiquetaDe(e.puntualidad) : ""}</div>` +
    `<p class="ayuda">Lectura: ${escapar(lectura.titulo)} · Enviado: ${escapar(fechaHoraLegible(e.fecha_hora_envio))} · Intentos: ${e.intentos}</p>` +
    preguntas.map((p, i) => `<div class="pregunta"><label>${i + 1}. ${escapar(p.enunciado)}</label>` +
      `<div class="respuesta-lectura">${escapar(e.respuestas[i] || "(sin respuesta)")}</div></div>`).join("") +
    `<form id="form-calificacion"><div class="campos"><div><label for="cal-nota">Calificación (0 a ${escapar(control.puntaje_maximo)})</label>` +
    `<input id="cal-nota" type="number" min="0" max="${escapar(control.puntaje_maximo)}" step="0.01" required value="${e.nota === null ? "" : escapar(e.nota)}"></div></div>` +
    `<label for="cal-retro">Retroalimentación</label><textarea id="cal-retro" rows="3">${escapar(e.retroalimentacion || "")}</textarea>` +
    `<label class="casilla"><input id="cal-publicar" type="checkbox" ${e.calificacion_publicada ? "checked" : ""}> Publicar al estudiante</label>` +
    `<button class="boton primario grande" type="submit">Guardar calificación</button></form>`;
  caja.hidden = false;
  caja.scrollIntoView({ behavior: "smooth", block: "start" });
  document.getElementById("form-calificacion").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try {
      await llamarApi(`/api/controles-lectura/${control.id}/calificacion`, { method: "POST", body: JSON.stringify({
        estudiante: e.estudiante,
        nota: document.getElementById("cal-nota").value,
        retroalimentacion: document.getElementById("cal-retro").value,
        publicar: document.getElementById("cal-publicar").checked,
      }) });
      mostrarMensaje("mensaje", "Calificación guardada");
      await cargarRevision();
    } catch (err) { error(err); }
  });
}

document.getElementById("revision-filas").addEventListener("click", async (evento) => {
  const boton = evento.target.closest("button[data-accion]");
  if (!boton) return;
  const indice = Number(boton.dataset.i);
  if (boton.dataset.accion === "revisar") return pintarRevisionDetalle(indice);
  try {
    await llamarApi(`/api/controles-lectura/${revisionActual.control.id}/nuevo-intento`, {
      method: "POST", body: JSON.stringify({ estudiante: revisionActual.estudiantes[indice].estudiante }) });
    mostrarMensaje("mensaje", "Nuevo intento habilitado");
    await cargarRevision();
  } catch (e) { error(e); }
});

selectControl.addEventListener("change", () => cargarRevision().catch(error));

agregarPregunta();
cargarLecturas().then(() => cargarControles()).catch(error);