/* VistaApuntesLectura: bibliografía, apuntes, dudas y respuesta a la pregunta de clase (lado del estudiante). */
const CLAVE_NOMBRE = "apuntes_lectura_nombre";
let estudiante = "";
let clase = null;                 // detalle de la clase abierta
let editando = null;              // { tipo: "apunte" | "duda", id }

const vistaLista = document.getElementById("lista-vista");
const vistaDetalle = document.getElementById("detalle-vista");
const nombreCodificado = () => encodeURIComponent(estudiante);
const mostrarError = (error) => mostrarMensaje("mensaje", error.message || "Ocurrió un error", "error");

function leerNombreGuardado() {
  try { return localStorage.getItem(CLAVE_NOMBRE) || ""; } catch (error) { return ""; }
}

function guardarNombre(nombre) {
  try { localStorage.setItem(CLAVE_NOMBRE, nombre); } catch (error) { /* sin almacenamiento: no pasa nada */ }
}

/* ---------- lista de clases ---------- */
function pintarLista(clases) {
  document.getElementById("lista-vacia").hidden = clases.length > 0;
  document.getElementById("lista").innerHTML = clases.map((c) =>
    `<li class="clase-item"><div><h3>${escapar(c.tema)}</h3>` +
    `<p>Bibliografía: ${c.bibliografia.map((l) => escapar(l.titulo)).join(" · ")}</p>` +
    `<p>Clase: ${escapar(fechaHoraLegible(c.inicio))} · Plazo para responder: ${escapar(fechaHoraLegible(c.cierre_respuesta))}</p>` +
    `<div class="etiquetas">${etiquetaDe(c.estado)}${c.puntualidad ? etiquetaDe(c.puntualidad) : ""}${etiquetaDe(c.ventana)}` +
    `${c.calificacion_publicada ? '<span class="etiqueta info">Calificada</span>' : ""}</div></div>` +
    `<button class="boton primario" type="button" data-id="${c.id}">Abrir</button></li>`).join("");
}

async function cargarLista() {
  pintarLista(await llamarApi(`/api/clases-lectura?estudiante=${nombreCodificado()}`));
  vistaDetalle.hidden = true;
  vistaLista.hidden = false;
}

/* ---------- detalle de la clase ---------- */
function pintarCabecera() {
  document.getElementById("det-cabecera").innerHTML =
    `<h2>${escapar(clase.tema)}</h2>` +
    `<div class="etiquetas">${etiquetaDe(clase.estado)}${clase.puntualidad ? etiquetaDe(clase.puntualidad) : ""}${etiquetaDe(clase.ventana)}</div>` +
    `<p class="ayuda">Clase: ${escapar(fechaHoraLegible(clase.inicio))} · Plazo para responder: ${escapar(fechaHoraLegible(clase.cierre_respuesta))}</p>`;
}

function pintarBibliografia() {
  document.getElementById("det-biblio").innerHTML = clase.bibliografia.map((l) =>
    `<li class="lectura-caja"><strong>${escapar(l.titulo)}</strong>` +
    `${l.autor ? `<span>${escapar(l.autor)}</span>` : ""}<span>${enlaceDeLectura(l)}</span></li>`).join("");
  document.getElementById("apunte-lectura").innerHTML = clase.bibliografia.map((l) =>
    `<option value="${l.id}">${escapar(l.titulo)}</option>`).join("");
}

function pintarNotas(contenedor, items, tipo) {
  const vacio = tipo === "apunte" ? "Todavía no tienes apuntes en esta clase." : "Todavía no anotaste dudas.";
  document.getElementById(contenedor).innerHTML = items.length ? items.map((item) => {
    const meta = `<div class="nota-meta"><span>${tipo === "apunte" ? "Texto: " + escapar(item.titulo_lectura) : "Duda"}</span>` +
      `<span>${escapar(fechaHoraLegible(item.actualizado))}</span></div>`;
    if (editando && editando.tipo === tipo && editando.id === item.id) {
      return `<li class="nota-item">${meta}<textarea rows="3" data-edicion="${tipo}-${item.id}">${escapar(item.texto)}</textarea>` +
        `<div class="nota-acciones"><button class="boton primario chico" type="button" data-accion="guardar" data-tipo="${tipo}" data-id="${item.id}">Guardar cambios</button>` +
        `<button class="boton secundario chico" type="button" data-accion="cancelar">Cancelar</button></div></li>`;
    }
    return `<li class="nota-item">${meta}<p>${escapar(item.texto)}</p><div class="nota-acciones">` +
      `<button class="boton secundario chico" type="button" data-accion="editar" data-tipo="${tipo}" data-id="${item.id}">Editar</button></div></li>`;
  }).join("") : `<li class="vacio">${vacio}</li>`;
}

function pintarCuaderno() {
  pintarNotas("lista-apuntes", clase.apuntes, "apunte");
  pintarNotas("lista-dudas", clase.dudas, "duda");
}

function pintarCalificacion() {
  if (!clase.calificacion_publicada) return "";
  return `<div class="calificacion"><div>Calificación: <strong>${escapar(clase.nota)}</strong> / ${escapar(clase.puntaje_maximo)}</div>` +
    `<div>${clase.retroalimentacion ? "Retroalimentación: " + escapar(clase.retroalimentacion) : "Sin retroalimentación escrita."}</div></div>`;
}

function pintarRespuesta(confirmacion = "") {
  const caja = document.getElementById("caja-respuesta");
  const respondido = clase.estado === "Respondido";
  let html = `<h2>4. Respuesta a la pregunta de clase</h2>` +
    `<p class="ayuda">La pregunta es aleatoria y la plantea tu docente en clase: el sistema no la muestra. ` +
    `Escribe el título derivado de la pregunta y tu respuesta, basándote en la lectura.</p>`;
  if (confirmacion) html += `<p class="confirmacion" role="status">${escapar(confirmacion)}. Estado: Respondido.</p>`;
  html += pintarCalificacion();
  if (clase.puede_responder) {
    html += respondido ? '<div class="advertencia" role="status"><p>El docente habilitó otro intento: reemplazará tu respuesta anterior.</p></div>' : "";
    html += clase.ventana === "Plazo vencido" ? '<div class="advertencia" role="status"><p>El plazo venció: tu respuesta se registrará como Tarde.</p></div>' : "";
    html += `<form id="form-respuesta" novalidate><div id="error-respuesta" class="advertencia error" role="alert" hidden></div>` +
      `<div id="campo-titulo"><label for="resp-titulo">Título derivado de la pregunta <span class="obligatoria" title="Obligatorio">*</span></label>` +
      `<input id="resp-titulo" maxlength="200" autocomplete="off"></div>` +
      `<div id="campo-respuesta"><label for="resp-texto">Tu respuesta <span class="obligatoria" title="Obligatorio">*</span></label>` +
      `<textarea id="resp-texto" rows="7"></textarea></div>` +
      `<p class="ayuda">Se entregará como PDF con la fecha y hora exactas del envío, marcada "A tiempo" o "Tarde". Tienes un solo intento.</p>` +
      `<button class="boton primario grande" type="submit">Enviar respuesta</button></form>`;
  } else if (respondido) {
    html += `<div class="etiquetas">${etiquetaDe(clase.estado)}${clase.puntualidad ? etiquetaDe(clase.puntualidad) : ""}</div>` +
      `<p class="ayuda">Enviada el ${escapar(fechaHoraExacta(clase.fecha_hora_envio))}. Solo el docente puede habilitar otro intento.</p>` +
      `<label>Título</label><div class="respuesta-lectura">${escapar(clase.titulo_respuesta)}</div>` +
      `<label>Respuesta</label><div class="respuesta-lectura">${escapar(clase.texto_respuesta)}</div>` +
      (clase.tiene_pdf ? `<a class="boton secundario" href="/api/clases-lectura/${clase.id}/respuesta/pdf?estudiante=${nombreCodificado()}" target="_blank" rel="noopener">Descargar mi PDF</a>` : "");
  } else {
    html += `<div class="advertencia" role="status"><p>Podrás responder cuando empiece la clase (${escapar(fechaHoraLegible(clase.inicio))}).</p></div>`;
  }
  caja.innerHTML = html;
  const formulario = document.getElementById("form-respuesta");
  if (formulario) formulario.addEventListener("submit", enviarRespuesta);
}

function pintarDetalle() {
  pintarCabecera();
  pintarBibliografia();
  pintarCuaderno();
  pintarRespuesta();
  vistaLista.hidden = true;
  vistaDetalle.hidden = false;
}

async function recargarClase() {
  clase = await llamarApi(`/api/clases-lectura/${clase.id}?estudiante=${nombreCodificado()}`);
}

async function abrirClase(id) {
  clase = { id };
  editando = null;
  await recargarClase();
  pintarDetalle();
}

/* ---------- apuntes y dudas ---------- */
document.getElementById("form-apunte").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const texto = document.getElementById("apunte-texto");
  try {
    await llamarApi(`/api/clases-lectura/${clase.id}/apuntes`, { method: "POST", body: JSON.stringify({
      estudiante, id_lectura: Number(document.getElementById("apunte-lectura").value), texto: texto.value }) });
    texto.value = "";
    await recargarClase();
    pintarCuaderno();
    mostrarMensaje("mensaje", "Apunte guardado");
  } catch (error) { mostrarError(error); }
});

document.getElementById("form-duda").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const texto = document.getElementById("duda-texto");
  try {
    await llamarApi(`/api/clases-lectura/${clase.id}/dudas`, { method: "POST", body: JSON.stringify({ estudiante, texto: texto.value }) });
    texto.value = "";
    await recargarClase();
    pintarCuaderno();
    mostrarMensaje("mensaje", "Duda guardada");
  } catch (error) { mostrarError(error); }
});

async function accionNota(evento) {
  const boton = evento.target.closest("button[data-accion]");
  if (!boton) return;
  const { accion, tipo } = boton.dataset;
  const id = Number(boton.dataset.id);
  if (accion === "editar") editando = { tipo, id };
  if (accion === "cancelar") editando = null;
  if (accion === "guardar") {
    const texto = document.querySelector(`[data-edicion="${tipo}-${id}"]`).value;
    try {
      await llamarApi(`/api/clases-lectura/${clase.id}/${tipo === "apunte" ? "apuntes" : "dudas"}/${id}`,
        { method: "PUT", body: JSON.stringify({ estudiante, texto }) });
      editando = null;
      await recargarClase();
      mostrarMensaje("mensaje", "Cambios guardados");
    } catch (error) { return mostrarError(error); }
  }
  pintarCuaderno();
}
document.getElementById("lista-apuntes").addEventListener("click", accionNota);
document.getElementById("lista-dudas").addEventListener("click", accionNota);

/* ---------- respuesta a la pregunta de clase ---------- */
async function enviarRespuesta(evento) {
  evento.preventDefault();
  const titulo = document.getElementById("resp-titulo").value;
  const respuesta = document.getElementById("resp-texto").value;
  const error = document.getElementById("error-respuesta");
  document.getElementById("campo-titulo").classList.toggle("campo-falta", !titulo.trim());
  document.getElementById("campo-respuesta").classList.toggle("campo-falta", !respuesta.trim());
  error.hidden = true;
  if (!titulo.trim() || !respuesta.trim()) {
    const faltan = [!titulo.trim() && "título", !respuesta.trim() && "respuesta"].filter(Boolean).join(" y ");
    error.innerHTML = `<p>Completa los campos obligatorios: ${faltan}</p>`;
    error.hidden = false;
    return;
  }
  const boton = evento.submitter;
  if (boton) boton.disabled = true;
  try {
    const resultado = await llamarApi(`/api/clases-lectura/${clase.id}/respuesta`, {
      method: "POST", body: JSON.stringify({ estudiante, titulo, respuesta }) });
    await recargarClase();
    pintarCabecera();
    pintarRespuesta(resultado.mensaje);
    mostrarMensaje("mensaje", resultado.mensaje);
  } catch (fallo) {
    if (boton) boton.disabled = false;
    error.innerHTML = `<p>${escapar(fallo.message || "No se pudo enviar la respuesta. Inténtalo de nuevo.")}</p>`;
    error.hidden = false;
    mostrarError(fallo);
  }
}

/* ---------- identidad y navegación ---------- */
async function identificarse(nombre) {
  const registrado = await llamarApi("/api/clases-lectura/estudiantes", { method: "POST", body: JSON.stringify({ nombre }) });
  estudiante = registrado.nombre;
  guardarNombre(estudiante);
  document.getElementById("nombre").value = estudiante;
  await cargarLista();
}

document.getElementById("identidad").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try { await identificarse(document.getElementById("nombre").value); } catch (error) { mostrarError(error); }
});

document.getElementById("lista").addEventListener("click", (evento) => {
  const boton = evento.target.closest("button[data-id]");
  if (boton) abrirClase(boton.dataset.id).catch(mostrarError);
});

document.getElementById("volver").addEventListener("click", () => cargarLista().catch(mostrarError));

const nombreGuardado = leerNombreGuardado();
if (nombreGuardado) identificarse(nombreGuardado).catch(() => {});