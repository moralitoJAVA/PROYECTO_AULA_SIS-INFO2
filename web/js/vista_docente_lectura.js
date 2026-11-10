/* VistaControlLectura: técnica del docente "leer antes, preguntar en clase, responder la pregunta sobre la lectura". */
const CLAVE_NOMBRE = "apuntes_lectura_nombre";      // misma clave que la vista "Apuntes y lectura": comparten identidad
const PREFIJO_MARCAS = "control_lectura:";
let estudiante = "";
let clases = [];
let clase = null;                                    // detalle de la clase elegida
let paso = 1;
let editandoFuente = null;                          // id de la fuente propia que se está editando

const selectClase = document.getElementById("clase-select");
const mostrarError = (error) => mostrarMensaje("mensaje", error.message || "Ocurrió un error", "error");
const nombreCodificado = () => encodeURIComponent(estudiante);

/* ---------- marcas personales (leído / duda explicada): solo en este navegador ---------- */
function claveMarcas(tipo) { return `${PREFIJO_MARCAS}${tipo}:${estudiante.toLowerCase()}:${clase.id}`; }

function leerMarcas(tipo) {
  try { return JSON.parse(localStorage.getItem(claveMarcas(tipo))) || []; } catch (error) { return []; }
}

function cambiarMarca(tipo, id, activa) {
  const marcas = new Set(leerMarcas(tipo));
  if (activa) marcas.add(id); else marcas.delete(id);
  try { localStorage.setItem(claveMarcas(tipo), JSON.stringify([...marcas])); } catch (error) { /* sin almacenamiento: no pasa nada */ }
}

function leerNombreGuardado() {
  try { return localStorage.getItem(CLAVE_NOMBRE) || ""; } catch (error) { return ""; }
}

function guardarNombre(nombre) {
  try { localStorage.setItem(CLAVE_NOMBRE, nombre); } catch (error) { /* idem */ }
}

/* ---------- encabezado de la clase y pasos ---------- */
function pintarResumen() {
  document.getElementById("clase-resumen").innerHTML =
    `<div class="resumen-clase">${etiquetaDe(clase.ventana)}${etiquetaDe(clase.estado)}` +
    `${clase.investigacion_libre ? '<span class="etiqueta info">Investigación libre</span>' : ""}` +
    `${clase.puntualidad ? etiquetaDe(clase.puntualidad) : ""}` +
    `<span>Clase: ${escapar(fechaHoraLegible(clase.inicio))}</span>` +
    `<span>Plazo para responder: ${escapar(fechaHoraLegible(clase.cierre_respuesta))}</span></div>`;
}

function pintarPasos() {
  const leidas = leerMarcas("leidas");
  const claves = [...clase.bibliografia.map((l) => `l${l.id}`), ...clase.fuentes.map((f) => `f${f.id}`)];
  const totalLecturas = claves.length;
  const leidasValidas = claves.filter((c) => leidas.includes(c)).length;
  const resueltas = leerMarcas("resueltas");
  const pendientes = clase.dudas.filter((d) => !resueltas.includes(d.id)).length;
  const respondido = clase.estado === "Respondido";

  document.getElementById("progreso-lectura").textContent = totalLecturas
    ? `${leidasValidas} de ${totalLecturas} fuentes leídas` : "Agrega las fuentes que encuentres";
  document.getElementById("progreso-dudas").textContent = clase.dudas.length
    ? `${pendientes} por preguntar · ${clase.dudas.length - pendientes} explicadas` : "Aún sin dudas anotadas";
  document.getElementById("progreso-respuesta").textContent = respondido
    ? (clase.calificacion_publicada ? "Respondida y calificada" : "Respondida") : "Pendiente de responder";

  const completos = { 1: totalLecturas > 0 && leidasValidas === totalLecturas, 2: clase.dudas.length > 0 && pendientes === 0, 3: respondido };
  document.querySelectorAll(".paso").forEach((boton) => {
    const numero = Number(boton.dataset.paso);
    boton.classList.toggle("completo", completos[numero]);
    boton.setAttribute("aria-selected", String(numero === paso));
    boton.querySelector(".paso-num").textContent = completos[numero] ? "✓" : String(numero);
  });
  [1, 2, 3].forEach((numero) => { document.getElementById(`panel-${numero}`).hidden = numero !== paso; });
}

/* ---------- paso 1: antes de la clase ---------- */
function tarjetaFuente({ clave, titulo, detalle, apuntes, atributo, id, editable }) {
  const esLeida = leerMarcas("leidas").includes(clave);
  const cabecera = editable && editandoFuente === id
    ? `<form class="form-fuente-editar" data-editar-fuente="${id}" novalidate>` +
      `<input aria-label="Título de la fuente" value="${escapar(titulo)}" maxlength="150" data-campo="titulo">` +
      `<input aria-label="Enlace de la fuente" type="url" value="${escapar(editable.enlace || "")}" data-campo="enlace" placeholder="https://...">` +
      `<div class="nota-acciones"><button class="boton primario chico" type="submit">Guardar cambios</button>` +
      `<button class="boton secundario chico" type="button" data-accion="cancelar-fuente">Cancelar</button></div></form>`
    : `<div><h3>${escapar(titulo)}</h3><p>${detalle}</p></div>` +
      `<div class="fila-acciones">${editable ? `<button class="boton secundario chico" type="button" data-accion="editar-fuente" data-id="${id}">Editar</button>` : ""}` +
      `<label class="casilla"><input type="checkbox" data-leida="${clave}" ${esLeida ? "checked" : ""}> Ya la leí</label></div>`;
  return `<li class="lectura-tarjeta${esLeida ? " leida" : ""}"><div class="lectura-cabecera">${cabecera}</div>` +
    `<ul class="lectura-apuntes">${apuntes.map((a) =>
      `<li class="nota-item"><div class="nota-meta"><span>Apunte</span><span>${escapar(fechaHoraLegible(a.actualizado))}</span></div>` +
      `<p>${escapar(a.texto)}</p></li>`).join("")}</ul>` +
    `<form class="form-apunte-rapido" ${atributo}="${id}" novalidate>` +
    `<textarea rows="2" aria-label="Nuevo apunte sobre ${escapar(titulo)}" placeholder="Idea principal, definición, ejemplo..."></textarea>` +
    `<button class="boton secundario chico" type="submit">Guardar apunte</button></form></li>`;
}

function pintarLecturas() {
  document.getElementById("bloque-docente").hidden = clase.bibliografia.length === 0;
  document.getElementById("lecturas").innerHTML = clase.bibliografia.map((l) => tarjetaFuente({
    clave: `l${l.id}`, titulo: l.titulo, id: l.id, atributo: "data-lectura",
    detalle: `${l.autor ? escapar(l.autor) + " · " : ""}${enlaceDeLectura(l)}`,
    apuntes: clase.apuntes.filter((a) => a.id_lectura === l.id) })).join("");
  document.getElementById("cuenta-fuentes").textContent = clase.fuentes.length;
  document.getElementById("fuentes").innerHTML = clase.fuentes.length ? clase.fuentes.map((f) => tarjetaFuente({
    clave: `f${f.id}`, titulo: f.titulo, id: f.id, atributo: "data-fuente", editable: f,
    detalle: f.enlace ? `<a href="${escapar(f.enlace)}" target="_blank" rel="noopener noreferrer">Abrir enlace</a>` : "Sin enlace",
    apuntes: clase.apuntes.filter((a) => a.id_fuente === f.id) })).join("")
    : '<li class="vacio">Todavía no registraste fuentes. Agrega la primera que encuentres.</li>';
}

/* ---------- paso 2: en clase ---------- */
function pintarDudas() {
  const resueltas = leerMarcas("resueltas");
  const fila = (duda) => {
    const hecha = resueltas.includes(duda.id);
    return `<li class="duda-item${hecha ? " resuelta" : ""}"><p>${escapar(duda.texto)}</p>` +
      `<label class="casilla"><input type="checkbox" data-resuelta="${duda.id}" ${hecha ? "checked" : ""}> Ya me la explicaron</label></li>`;
  };
  const pendientes = clase.dudas.filter((d) => !resueltas.includes(d.id));
  const hechas = clase.dudas.filter((d) => resueltas.includes(d.id));
  document.getElementById("dudas-pendientes").innerHTML = pendientes.length ? pendientes.map(fila).join("")
    : `<li class="vacio">${clase.dudas.length ? "No te quedan dudas por preguntar." : "Todavía no anotaste dudas."}</li>`;
  document.getElementById("dudas-resueltas").innerHTML = hechas.length ? hechas.map(fila).join("")
    : '<li class="vacio">Aquí aparecerán las dudas que el docente ya te explicó.</li>';
  document.getElementById("cuenta-pendientes").textContent = pendientes.length;
  document.getElementById("cuenta-resueltas").textContent = hechas.length;
}

/* ---------- paso 3: pregunta del docente sobre la lectura ---------- */
function pintarCalificacion() {
  if (!clase.calificacion_publicada) return "";
  return `<div class="calificacion"><div>Calificación: <strong>${escapar(clase.nota)}</strong> / ${escapar(clase.puntaje_maximo)}</div>` +
    `<div>${clase.retroalimentacion ? "Retroalimentación: " + escapar(clase.retroalimentacion) : "Sin retroalimentación escrita."}</div></div>`;
}

function pintarRespuesta(confirmacion = "") {
  const respondido = clase.estado === "Respondido";
  let html = `<h2>Pregunta del docente sobre la lectura</h2>` +
    `<p class="ayuda">A veces el docente te pregunta sobre lo leído. La pregunta la plantea en clase y el sistema no la muestra: ` +
    `escribe el título derivado de la pregunta y tu respuesta, basándote en la lectura.</p>`;
  if (confirmacion) html += `<p class="confirmacion" role="status">${escapar(confirmacion)}. Estado: Respondido.</p>`;
  html += pintarCalificacion();
  if (clase.puede_responder) {
    if (respondido) html += '<div class="advertencia" role="status"><p>El docente habilitó otro intento: reemplazará tu respuesta anterior.</p></div>';
    if (clase.ventana === "Plazo vencido") html += '<div class="advertencia" role="status"><p>El plazo venció: tu respuesta se registrará como Tarde.</p></div>';
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
  document.getElementById("panel-3").innerHTML = html;
  const formulario = document.getElementById("form-respuesta");
  if (formulario) formulario.addEventListener("submit", enviarRespuesta);
}

function pintarTodo() {
  pintarResumen();
  pintarLecturas();
  pintarDudas();
  pintarRespuesta();
  pintarPasos();
}

/* ---------- carga de datos ---------- */
function pasoSugerido() {
  if (clase.estado === "Respondido") return 3;
  return clase.ventana === "Antes de la clase" ? 1 : 2;
}

async function recargarClase() {
  clase = await llamarApi(`/api/clases-lectura/${clase.id}?estudiante=${nombreCodificado()}`);
}

async function abrirClase(id) {
  clase = { id };
  editandoFuente = null;
  await recargarClase();
  paso = pasoSugerido();
  pintarTodo();
}

function claseInicial() {
  const enCurso = clases.find((c) => c.ventana === "Dentro del plazo");
  const proxima = clases.find((c) => c.ventana === "Antes de la clase");
  return (enCurso || proxima || clases[clases.length - 1]).id;
}

async function cargarClases() {
  clases = await llamarApi(`/api/clases-lectura?estudiante=${nombreCodificado()}`);
  document.getElementById("tablero").hidden = false;
  const hay = clases.length > 0;
  document.getElementById("sin-clases").hidden = hay;
  document.getElementById("selector-clase").hidden = !hay;
  document.getElementById("pasos").hidden = !hay;
  [1, 2, 3].forEach((n) => { document.getElementById(`panel-${n}`).hidden = true; });
  if (!hay) return;
  selectClase.innerHTML = clases.map((c) => `<option value="${c.id}">${escapar(c.tema)}</option>`).join("");
  selectClase.value = String(claseInicial());
  await abrirClase(selectClase.value);
}

/* ---------- acciones ---------- */
const panelUno = document.getElementById("panel-1");

panelUno.addEventListener("change", (evento) => {
  const casilla = evento.target.closest("input[data-leida]");
  if (!casilla) return;
  cambiarMarca("leidas", casilla.dataset.leida, casilla.checked);
  pintarLecturas();
  pintarPasos();
});

panelUno.addEventListener("click", (evento) => {
  const boton = evento.target.closest("button[data-accion]");
  if (!boton) return;
  if (boton.dataset.accion === "editar-fuente") editandoFuente = Number(boton.dataset.id);
  if (boton.dataset.accion === "cancelar-fuente") editandoFuente = null;
  pintarLecturas();
});

panelUno.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const base = `/api/clases-lectura/${clase.id}`;
  try {
    const apunte = evento.target.closest("form.form-apunte-rapido");
    const edicion = evento.target.closest("form[data-editar-fuente]");
    if (apunte) {
      const cuerpo = { estudiante, texto: apunte.querySelector("textarea").value };
      if (apunte.dataset.lectura) cuerpo.id_lectura = Number(apunte.dataset.lectura);
      else cuerpo.id_fuente = Number(apunte.dataset.fuente);
      await llamarApi(`${base}/apuntes`, { method: "POST", body: JSON.stringify(cuerpo) });
      mostrarMensaje("mensaje", "Apunte guardado");
    } else if (edicion) {
      await llamarApi(`${base}/fuentes/${edicion.dataset.editarFuente}`, { method: "PUT", body: JSON.stringify({
        estudiante, titulo: edicion.querySelector('[data-campo="titulo"]').value, enlace: edicion.querySelector('[data-campo="enlace"]').value }) });
      editandoFuente = null;
      mostrarMensaje("mensaje", "Fuente actualizada");
    } else if (evento.target.id === "form-fuente") {
      const titulo = document.getElementById("fuente-titulo");
      const enlace = document.getElementById("fuente-enlace");
      await llamarApi(`${base}/fuentes`, { method: "POST", body: JSON.stringify({ estudiante, titulo: titulo.value, enlace: enlace.value }) });
      titulo.value = "";
      enlace.value = "";
      mostrarMensaje("mensaje", "Fuente agregada");
    } else return;
    await recargarClase();
    pintarLecturas();
    pintarPasos();
  } catch (error) { mostrarError(error); }
});

document.getElementById("form-duda").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const texto = document.getElementById("duda-texto");
  try {
    const enviado = texto.value;
    await llamarApi(`/api/clases-lectura/${clase.id}/dudas`, { method: "POST", body: JSON.stringify({ estudiante, texto: enviado }) });
    if (texto.value === enviado) texto.value = "";      // no borrar lo que la persona siguió escribiendo mientras se guardaba
    await recargarClase();
    pintarDudas();
    pintarPasos();
    mostrarMensaje("mensaje", "Duda agregada");
  } catch (error) { mostrarError(error); }
});

function alternarDuda(evento) {
  const casilla = evento.target.closest("input[data-resuelta]");
  if (!casilla) return;
  cambiarMarca("resueltas", Number(casilla.dataset.resuelta), casilla.checked);
  pintarDudas();
  pintarPasos();
}
document.getElementById("dudas-pendientes").addEventListener("change", alternarDuda);
document.getElementById("dudas-resueltas").addEventListener("change", alternarDuda);

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
    pintarResumen();
    pintarRespuesta(resultado.mensaje);
    pintarPasos();
    mostrarMensaje("mensaje", resultado.mensaje);
  } catch (fallo) {
    if (boton) boton.disabled = false;
    error.innerHTML = `<p>${escapar(fallo.message || "No se pudo enviar la respuesta. Inténtalo de nuevo.")}</p>`;
    error.hidden = false;
    mostrarError(fallo);
  }
}

document.getElementById("pasos").addEventListener("click", (evento) => {
  const boton = evento.target.closest(".paso");
  if (!boton || !clase) return;
  paso = Number(boton.dataset.paso);
  pintarPasos();
});

selectClase.addEventListener("change", () => abrirClase(selectClase.value).catch(mostrarError));

/* ---------- identidad ---------- */
async function identificarse(nombre) {
  const registrado = await llamarApi("/api/clases-lectura/estudiantes", { method: "POST", body: JSON.stringify({ nombre }) });
  estudiante = registrado.nombre;
  guardarNombre(estudiante);
  document.getElementById("nombre").value = estudiante;
  await cargarClases();
}

document.getElementById("identidad").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try { await identificarse(document.getElementById("nombre").value); } catch (error) { mostrarError(error); }
});

const nombreGuardado = leerNombreGuardado();
if (nombreGuardado) identificarse(nombreGuardado).catch(() => {});
