/* VistaDocenteLectura: apoyo mínimo a la app del estudiante (bibliografía, clases, calificación, nuevo intento). */
const selectClase = document.getElementById("revision-clase");
let revisionActual = null;

function error(e) { mostrarMensaje("mensaje", e.message || "Ocurrió un error", "error"); }

// ---------- bibliografía ----------
async function cargarLecturas() {
  const lecturas = await llamarApi("/api/lecturas");
  document.getElementById("clase-lecturas").innerHTML = lecturas.length
    ? lecturas.map((l) => `<label class="casilla"><input type="checkbox" name="lectura" value="${l.id}"> ${escapar(l.titulo)}${l.autor ? " — " + escapar(l.autor) : ""}</label>`).join("")
    : '<p class="ayuda">Primero registra un texto de bibliografía.</p>';
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
    mostrarMensaje("mensaje", "Texto registrado");
  } catch (e) { error(e); }
});

// ---------- clases ----------
document.getElementById("form-clase").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    await llamarApi("/api/clases-lectura", { method: "POST", body: JSON.stringify({
      tema: document.getElementById("clase-tema").value,
      inicio: document.getElementById("clase-inicio").value,
      cierre_respuesta: document.getElementById("clase-cierre").value,
      ids_lecturas: [...document.querySelectorAll('input[name="lectura"]:checked')].map((c) => Number(c.value)),
    }) });
    evento.target.reset();
    mostrarMensaje("mensaje", "Clase publicada");
    await cargarClases(true);
  } catch (e) { error(e); }
});

// ---------- revisión ----------
async function cargarClases(seleccionarUltima = false) {
  const clases = await llamarApi("/api/clases-lectura");
  selectClase.innerHTML = clases.length
    ? clases.map((c) => `<option value="${c.id}">${escapar(c.tema)}</option>`).join("")
    : '<option value="">Aún no hay clases publicadas</option>';
  if (clases.length && seleccionarUltima) selectClase.value = String(Math.max(...clases.map((c) => c.id)));
  await cargarRevision();
}

async function cargarRevision() {
  document.getElementById("revision-detalle").hidden = true;
  const id = selectClase.value;
  const filas = document.getElementById("revision-filas");
  if (!id) {
    revisionActual = null; filas.innerHTML = "";
    document.getElementById("tabla-caja").hidden = true; document.getElementById("revision-vacia").hidden = true;
    return;
  }
  revisionActual = await llamarApi(`/api/clases-lectura/${id}/respuestas`);
  const lista = revisionActual.estudiantes;
  document.getElementById("revision-vacia").hidden = lista.length > 0;
  document.getElementById("tabla-caja").hidden = lista.length === 0;
  filas.innerHTML = lista.map((e, i) =>
    `<tr><td>${escapar(e.estudiante)}</td><td>${etiquetaDe(e.estado_revision)}${e.intento_habilitado ? ' <span class="etiqueta info">Nuevo intento habilitado</span>' : ""}</td>` +
    `<td>${e.fecha_hora_envio ? escapar(fechaHoraExacta(e.fecha_hora_envio)) : "—"}</td>` +
    `<td class="num">${e.nota === null ? "—" : escapar(e.nota)}${e.nota !== null && e.calificacion_publicada ? " ✓" : ""}</td>` +
    `<td><div class="fila-acciones"><button class="boton secundario chico" type="button" data-accion="revisar" data-i="${i}" ${e.fecha_hora_envio ? "" : "disabled"}>Revisar</button>` +
    `<button class="boton secundario chico" type="button" data-accion="intento" data-i="${i}">Habilitar nuevo intento</button></div></td></tr>`
  ).join("");
}

function pintarRevisionDetalle(indice) {
  const e = revisionActual.estudiantes[indice];
  const { clase } = revisionActual;
  const caja = document.getElementById("revision-detalle");
  caja.innerHTML = `<h2>${escapar(e.estudiante)} — ${escapar(clase.tema)}</h2>` +
    `<div class="etiquetas">${etiquetaDe(e.estado_revision)}${e.puntualidad ? etiquetaDe(e.puntualidad) : ""}</div>` +
    `<p class="ayuda">Enviado: ${escapar(fechaHoraExacta(e.fecha_hora_envio))} · Intentos: ${e.intentos} · ` +
    `<a href="/api/clases-lectura/${clase.id}/respuesta/pdf?estudiante=${encodeURIComponent(e.estudiante)}" target="_blank" rel="noopener">Abrir PDF</a></p>` +
    `<label>Título</label><div class="respuesta-lectura">${escapar(e.titulo)}</div>` +
    `<label>Respuesta</label><div class="respuesta-lectura">${escapar(e.respuesta)}</div>` +
    `<form id="form-calificacion"><div class="campos"><div><label for="cal-nota">Calificación (0 a 100)</label>` +
    `<input id="cal-nota" type="number" min="0" max="100" step="0.01" required value="${e.nota === null ? "" : escapar(e.nota)}"></div></div>` +
    `<label for="cal-retro">Retroalimentación</label><textarea id="cal-retro" rows="3">${escapar(e.retroalimentacion || "")}</textarea>` +
    `<label class="casilla"><input id="cal-publicar" type="checkbox" ${e.calificacion_publicada ? "checked" : ""}> Publicar al estudiante</label>` +
    `<button class="boton primario grande" type="submit">Guardar calificación</button></form>`;
  caja.hidden = false;
  caja.scrollIntoView({ behavior: "smooth", block: "start" });
  document.getElementById("form-calificacion").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try {
      await llamarApi(`/api/clases-lectura/${clase.id}/calificacion`, { method: "POST", body: JSON.stringify({
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
    await llamarApi(`/api/clases-lectura/${revisionActual.clase.id}/nuevo-intento`, {
      method: "POST", body: JSON.stringify({ estudiante: revisionActual.estudiantes[indice].estudiante }) });
    mostrarMensaje("mensaje", "Nuevo intento habilitado");
    await cargarRevision();
  } catch (e) { error(e); }
});

selectClase.addEventListener("change", () => cargarRevision().catch(error));

cargarLecturas().then(() => cargarClases()).catch(error);