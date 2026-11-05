const MS_MINUTO = 60000;
const MS_HORA = 60 * MS_MINUTO;
const MS_DIA = 24 * MS_HORA;
const VENTANA_BARRA = 7 * MS_DIA; // la barra se llena durante la última semana
const DURACION_AVISO = 6000;

let tareas = [];
let porVencer = [];
let filtro = "";
let detalle = null;
let apuntes = [];
let adjuntos = [];
let integrantes = [];
let disparador = null;
let temporizadorAviso = null;

const $ = (id) => document.getElementById(id);

/* ---------- Utilidades ---------- */

function esEnlace(texto) {
  return texto.startsWith("http://") || texto.startsWith("https://");
}

function esDescargable(ruta) {
  return esEnlace(ruta) || ruta.startsWith("/");
}

function atributo(texto) {
  return escapar(texto).replace(/"/g, "&quot;");
}

function parsear(iso) {
  return new Date(iso.slice(0, 19));
}

function dosDigitos(n) {
  return String(n).padStart(2, "0");
}

function formatoFecha(iso) {
  const f = parsear(iso);
  const dia = f.toLocaleDateString("es", { weekday: "short", day: "numeric", month: "short" });
  return `${dia}, ${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}`;
}

function formatoExacto(iso) {
  const f = parsear(iso);
  return `${dosDigitos(f.getDate())}/${dosDigitos(f.getMonth() + 1)}/${f.getFullYear()} a las ` +
    `${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}:${dosDigitos(f.getSeconds())}`;
}

function duracion(ms) {
  const dias = Math.floor(ms / MS_DIA);
  if (dias >= 1) return `${dias} ${dias === 1 ? "día" : "días"}`;
  const horas = Math.floor(ms / MS_HORA);
  if (horas >= 1) return `${horas} h`;
  return `${Math.max(1, Math.floor(ms / MS_MINUTO))} min`;
}

function tiempoRestante(iso) {
  const ms = parsear(iso) - Date.now();
  const proporcion = Math.min(1, Math.max(0, 1 - ms / VENTANA_BARRA));
  if (ms < 0) return { cifra: "Vencida", unidad: "", nota: "hace " + duracion(-ms), vencida: true, proporcion: 1 };
  if (ms < MS_HORA) {
    return { cifra: String(Math.max(1, Math.ceil(ms / MS_MINUTO))), unidad: "min", nota: "restantes", proporcion };
  }
  if (ms < MS_DIA) {
    const minutos = Math.floor((ms % MS_HORA) / MS_MINUTO);
    return { cifra: String(Math.floor(ms / MS_HORA)), unidad: "h", nota: `${minutos} min más`, proporcion };
  }
  const dias = Math.floor(ms / MS_DIA);
  const horas = Math.floor((ms % MS_DIA) / MS_HORA);
  return { cifra: String(dias), unidad: dias === 1 ? "día" : "días", nota: `${horas} h más`, proporcion };
}

/* ---------- Iconos ---------- */

const ICONOS = {
  persona: '<path d="M4 17c.6-3.4 3.2-5.2 6-5.2s5.4 1.8 6 5.2"/><circle cx="10" cy="6.5" r="3.2"/>',
  grupo: '<circle cx="7" cy="7" r="2.8"/><path d="M1.5 16.5c.5-3 2.6-4.6 5.5-4.6s5 1.6 5.5 4.6"/><circle cx="14" cy="7.5" r="2.4"/><path d="M14 12c2.4 0 4 1.3 4.5 4"/>',
  reloj: '<circle cx="10" cy="10" r="7.5"/><path d="M10 5.5V10l3 2"/>',
  calendario: '<rect x="3" y="4.5" width="14" height="12.5" rx="2"/><path d="M3 8.5h14M7 2.5v3M13 2.5v3"/>',
  check: '<circle cx="10" cy="10" r="7.5"/><path d="M6.5 10.3l2.4 2.4 4.6-5"/>',
  nota: '<path d="M10 2.5l2.2 4.6 5 .7-3.6 3.5.9 5L10 13.9l-4.5 2.4.9-5L2.8 7.8l5-.7z"/>',
  descargar: '<path d="M10 3v10m0 0l-4-4m4 4l4-4M3.5 16.5h13"/>',
  cerrar: '<path d="M5 5l10 10M15 5L5 15"/>',
};

function icono(nombre) {
  return `<svg class="icono" viewBox="0 0 20 20" aria-hidden="true">${ICONOS[nombre]}</svg>`;
}

/* ---------- Lista ---------- */

function claseDeEstado(estado) {
  return estado.toLowerCase();
}

function relojHtml(t, urgente) {
  if (t.estado === "Calificada") {
    return `<span class="reloj"><span class="reloj-cifra">${escapar(t.nota_final)}</span><span class="reloj-nota">nota final</span></span>`;
  }
  if (t.estado === "Entregada") {
    return `<span class="reloj">${icono("check")}<span class="reloj-nota">esperando nota</span></span>`;
  }
  const r = tiempoRestante(t.fecha_limite);
  const unidad = r.unidad ? `<small>${r.unidad}</small>` : "";
  return `<span class="reloj"><span class="reloj-cifra${r.vencida ? " texto" : ""}">${r.cifra}${unidad}</span>` +
    `<span class="reloj-nota">${escapar(r.nota)}</span>` +
    `<span class="reloj-barra"><i style="width:${Math.round(r.proporcion * 100)}%"></i></span></span>`;
}

function etiquetasHtml(t, urgente) {
  const etiquetas = [];
  if (t.estado === "Pendiente") {
    const vencida = tiempoRestante(t.fecha_limite).vencida;
    if (vencida) etiquetas.push('<span class="etiqueta">Plazo vencido</span>');
    else if (urgente) etiquetas.push('<span class="etiqueta urgente">Vence pronto</span>');
    else etiquetas.push('<span class="etiqueta">Pendiente</span>');
  } else {
    etiquetas.push(`<span class="etiqueta ${claseDeEstado(t.estado)}">${escapar(t.estado)}</span>`);
  }
  if (Number(t.descuento) > 0 && t.estado !== "Pendiente") {
    etiquetas.push(`<span class="etiqueta descuento">−${escapar(t.descuento)}%</span>`);
  }
  return etiquetas.join("");
}

function filaHtml(t) {
  const urgente = t.estado === "Pendiente" && porVencer.includes(t.numero);
  const vencida = t.estado === "Pendiente" && tiempoRestante(t.fecha_limite).vencida;
  const clases = ["fila", claseDeEstado(t.estado)];
  if (urgente) clases.push("urgente");
  if (vencida) clases.push("vencida");
  const grupal = t.tipo === "Grupal";
  return `<li><button class="${clases.join(" ")}" data-numero="${t.numero}">` +
    relojHtml(t, urgente) +
    `<span class="fila-cuerpo"><span class="fila-titulo">${escapar(t.titulo)}</span>` +
    `<span class="fila-meta"><span>${icono(grupal ? "grupo" : "persona")}${escapar(t.tipo)}</span>` +
    `<span>${icono("calendario")}Límite: ${escapar(formatoFecha(t.fecha_limite))}</span></span></span>` +
    `<span class="fila-lado">${etiquetasHtml(t, urgente)}</span></button></li>`;
}

const MENSAJES_VACIO = {
  "": ["Todavía no tienes tareas", "Cuando el docente registre una tarea, aparecerá aquí."],
  Pendiente: ["No tienes tareas pendientes", "Todo lo que te asignaron ya está entregado."],
  Entregada: ["No hay tareas entregadas sin calificar", "Las tareas que entregues aparecerán aquí hasta que registres su nota."],
  Calificada: ["Aún no registras calificaciones", "Cuando recibas la nota de una tarea, regístrala desde su detalle."],
};

function pintarLista() {
  const visibles = filtro ? tareas.filter((t) => t.estado === filtro) : tareas;
  $("lista").innerHTML = visibles.map(filaHtml).join("");
  const vacio = $("vacio");
  vacio.hidden = visibles.length > 0;
  if (!visibles.length) {
    const [titulo, texto] = MENSAJES_VACIO[filtro];
    vacio.innerHTML = `<strong>${titulo}</strong>${texto}`;
  }
  document.querySelectorAll("[data-cuenta]").forEach((nodo) => {
    const estado = nodo.dataset.cuenta;
    nodo.textContent = estado ? tareas.filter((t) => t.estado === estado).length : tareas.length;
  });
  document.querySelectorAll(".filtro").forEach((boton) =>
    boton.setAttribute("aria-pressed", String(boton.dataset.estado === filtro)));
  pintarAdvertencia();
}

function pintarAdvertencia() {
  const caja = $("advertencia");
  const urgentes = tareas.filter((t) => t.estado === "Pendiente" && porVencer.includes(t.numero));
  caja.hidden = urgentes.length === 0;
  if (!urgentes.length) return;
  caja.innerHTML = `${icono("reloj")}<div><p>Vence en menos de 24 horas</p><ul>` +
    urgentes.map((t) => `<li><button data-numero="${t.numero}">${escapar(t.titulo)}</button></li>`).join("") +
    "</ul></div>";
}

async function cargarLista() {
  const datos = await llamarApi("/api/tareas");
  tareas = datos.tareas;
  porVencer = datos.por_vencer;
  pintarLista();
}

/* ---------- Detalle ---------- */

function pasosHtml(estado) {
  const nombres = ["Pendiente", "Entregada", "Calificada"];
  const actual = nombres.indexOf(estado);
  return '<ol class="pasos" aria-label="Avance de la tarea">' + nombres.map((nombre, i) => {
    const clase = i < actual ? "hecho" : i === actual ? "actual" + (i === 2 ? " final" : "") : "";
    return `<li class="${clase}"${i === actual ? ' aria-current="step"' : ""}>${nombre}</li>`;
  }).join("") + "</ol>";
}

function listaAdjuntosHtml(entrega) {
  const items = [
    ...entrega.archivos.map((a) => `<li>${escapar(a)}</li>`),
    ...entrega.enlaces.map((e) => `<li><a href="${atributo(e)}" target="_blank" rel="noopener noreferrer">${escapar(e)}</a></li>`),
  ];
  return `<ul class="adjuntos-lista">${items.join("")}</ul>`;
}

function formularioEntregaHtml(tarea, grupal) {
  const vencida = tiempoRestante(tarea.fecha_limite).vencida;
  if (vencida) {
    return `<section class="bloque"><h3>Tu entrega</h3>` +
      `<p class="nota-vencida">El plazo venció el ${escapar(formatoFecha(tarea.fecha_limite))}. Ya no se puede entregar esta tarea.</p></section>`;
  }
  const equipo = grupal ? `
    <label for="integrante">Integrantes del equipo <span class="ayuda" id="cuenta-equipo"></span></label>
    <p class="ayuda">El primero eres tú y entregas por todo el equipo. Marca a quien no cumplió su parte para penalizar su nota.</p>
    <div class="campo-linea">
      <input id="integrante" autocomplete="off">
      <button type="button" class="boton secundario" id="agregar-integrante">Agregar</button>
    </div>
    <ul id="integrantes" class="equipo"></ul>` : "";
  return `<section class="bloque">
    <h3>Tu entrega</h3>
    <label for="adjunto">Archivo o enlace</label>
    <div class="campo-linea">
      <input id="adjunto" placeholder="informe.pdf o https://github.com/..." autocomplete="off">
      <button type="button" class="boton secundario" id="agregar-adjunto">Agregar</button>
    </div>
    <ul id="adjuntos" class="chips"></ul>
    ${equipo}
    <div id="error-entrega" class="error-inline" role="alert" hidden></div>
    <button type="button" class="boton primario grande" id="entregar">${grupal ? "Entregar por el equipo" : "Entregar tarea"}</button>
  </section>`;
}

function confirmacionHtml(entrega, equipo) {
  const quienes = equipo ? equipo.integrantes.map((n, i) => {
    const incumple = equipo.incumplen.includes(n);
    return `${escapar(n)}${i === 0 ? " (tú)" : ""}${incumple ? " · no cumplió" : ""}`;
  }).join(", ") : "";
  return `<section class="bloque">
    <h3>Entrega confirmada</h3>
    <p><span class="sello">Entregada el ${escapar(formatoExacto(entrega.fecha_hora_entrega))}</span></p>
    ${listaAdjuntosHtml(entrega)}
    ${quienes ? `<p class="ayuda" style="margin-top:12px">Equipo: ${quienes}</p>` : ""}
  </section>`;
}

function penalizacionHtml(penalizacion) {
  if (!penalizacion) return "";
  return `<section class="bloque"><div class="penalizacion" style="margin-top:0"><strong>Penalización aplicada</strong>` +
    `<p>${escapar(penalizacion.motivo)}</p></div></section>`;
}

function formularioNotaHtml(maximo) {
  return `<section class="bloque">
    <h3>Registrar la calificación recibida</h3>
    <div class="dos-col">
      <div><label for="nota">Nota <span class="ayuda">máximo ${escapar(maximo)}</span></label>
        <input id="nota" type="number" min="0" max="${atributo(maximo)}" step="0.01" inputmode="decimal"></div>
      <div><label for="escala">Escala de evaluación</label><input id="escala" value="0-100"></div>
    </div>
    <label for="comentarios">Comentarios del docente</label>
    <textarea id="comentarios" rows="3"></textarea>
    <div id="error-nota" class="error-inline" role="alert" hidden></div>
    <button type="button" class="boton primario grande" id="calificar">Guardar calificación</button>
  </section>`;
}

function resultadoHtml(entrega, maximo, fila) {
  const descuento = Number(entrega.descuento) > 0;
  return `<section class="bloque resultado">
    <h3>Tu calificación</h3>
    <div class="nota-grande"><span>${escapar(entrega.nota)}</span><small>de ${escapar(maximo)}</small></div>
    <dl>
      <dt>Escala</dt><dd>${escapar(entrega.escala || "")}</dd>
      ${descuento ? `<dt>Descuento</dt><dd>${escapar(entrega.descuento)}%</dd>` : ""}
      ${fila && fila.nota_final ? `<dt>Nota final</dt><dd>${escapar(fila.nota_final)}</dd>` : ""}
    </dl>
    <p class="comentario">${entrega.comentarios ? escapar(entrega.comentarios) : "Sin comentarios."}</p>
  </section>`;
}

function pintarDetalle() {
  const { tarea, entrega, puntaje_maximo: maximo, equipo, penalizacion } = detalle;
  const fila = tareas.find((t) => t.numero === tarea.numero);
  const grupal = tarea.tipo === "Grupal";
  const estado = entrega.estado;
  const recurso = tarea.ruta_adjunto
    ? (esDescargable(tarea.ruta_adjunto)
      ? `<a class="boton secundario" href="${atributo(tarea.ruta_adjunto)}" download>${icono("descargar")}Descargar guía</a>`
      : `<span>${escapar(tarea.ruta_adjunto)}</span>`)
    : "";
  let cuerpo = "";
  if (estado === "Pendiente") cuerpo += formularioEntregaHtml(tarea, grupal);
  else cuerpo += confirmacionHtml(entrega, equipo) + penalizacionHtml(penalizacion);
  if (estado === "Entregada") cuerpo += formularioNotaHtml(maximo);
  if (estado === "Calificada") cuerpo += resultadoHtml(entrega, maximo, fila);

  $("detalle-contenido").innerHTML = `
    <div class="panel-cabecera">
      <p class="panel-codigo">${escapar(tarea.codigo || "")}</p>
      <h2 id="detalle-titulo" tabindex="-1">${escapar(tarea.titulo)}</h2>
      <div class="panel-meta">
        <span>${icono(grupal ? "grupo" : "persona")}${escapar(tarea.tipo)}</span>
        <span>${icono("calendario")}Límite: ${escapar(formatoFecha(tarea.fecha_limite))}</span>
      </div>
      <button type="button" class="cerrar" data-cerrar aria-label="Cerrar detalle">${icono("cerrar")}</button>
    </div>
    ${pasosHtml(estado)}
    <section class="bloque">
      <h3>Instrucciones</h3>
      <p class="instrucciones">${escapar(tarea.instrucciones || "Sin instrucciones.")}</p>
      <div class="datos"><span>Puntaje máximo <strong>${escapar(maximo)}</strong></span>${recurso}</div>
    </section>
    ${cuerpo}
    <section class="bloque">
      <h3>Mis apuntes</h3>
      <ul id="apuntes" class="apuntes"></ul>
      <label for="apunte">Nuevo apunte</label>
      <textarea id="apunte" rows="2" placeholder="Escribe un apunte sobre esta tarea"></textarea>
      <div id="error-apunte" class="error-inline" role="alert" hidden></div>
      <button type="button" class="boton secundario" id="guardar-apunte" style="margin-top:10px">Guardar apunte</button>
    </section>`;
  pintarAdjuntos();
  pintarEquipo();
  pintarApuntes();
}

function pintarAdjuntos() {
  const lista = $("adjuntos");
  if (!lista) return;
  lista.innerHTML = adjuntos.map((a, i) =>
    `<li><span>${escapar(a)}</span><button type="button" class="quitar" data-quitar-adjunto="${i}" aria-label="Quitar ${atributo(a)}">${icono("cerrar")}</button></li>`).join("");
}

function pintarEquipo() {
  const lista = $("integrantes");
  if (!lista) return;
  lista.innerHTML = integrantes.map((p, i) =>
    `<li class="${p.incumple ? "incumple" : ""}"><span class="nombre">${escapar(p.nombre)}${i === 0 ? " <em>(tú)</em>" : ""}</span>` +
    `<label class="marca"><input type="checkbox" data-incumple="${i}"${p.incumple ? " checked" : ""}>No cumplió</label>` +
    `<button type="button" class="quitar" data-quitar-integrante="${i}" aria-label="Quitar a ${atributo(p.nombre)}">${icono("cerrar")}</button></li>`).join("");
  $("cuenta-equipo").textContent = `${integrantes.length} de ${detalle.tarea.tamano_equipo}`;
  $("integrante").placeholder = integrantes.length ? "Nombre del integrante" : "Tu nombre";
}

function pintarApuntes() {
  const lista = $("apuntes");
  if (!lista) return;
  lista.innerHTML = apuntes.length
    ? apuntes.map((a) => `<li><span>${escapar(a.texto)}</span><button type="button" data-borrar-apunte="${atributo(a.clave)}">Borrar</button></li>`).join("")
    : '<li style="background:none;padding:0;color:var(--tinta-suave)"><span>Aún no tienes apuntes para esta tarea.</span></li>';
}

/* ---------- Abrir y cerrar ---------- */

async function abrirDetalle(numero, origen) {
  disparador = origen || document.activeElement;
  try {
    detalle = await llamarApi("/api/tareas/" + numero);
    apuntes = await llamarApi("/api/apuntes?vinculo=tarea-" + numero);
  } catch (error) {
    avisar(error.message, "error");
    return;
  }
  adjuntos = [];
  integrantes = [];
  pintarDetalle();
  $("fondo").hidden = false;
  const panel = $("detalle");
  panel.setAttribute("aria-hidden", "false");
  panel.classList.add("abierto");
  panel.scrollTop = 0;
  $("detalle-titulo").focus();
}

function cerrarDetalle() {
  const panel = $("detalle");
  if (!panel.classList.contains("abierto")) return;
  panel.classList.remove("abierto");
  panel.setAttribute("aria-hidden", "true");
  $("fondo").hidden = true;
  if (disparador && document.contains(disparador)) disparador.focus();
}

async function refrescarDetalle() {
  const numero = detalle.tarea.numero;
  await cargarLista();
  detalle = await llamarApi("/api/tareas/" + numero);
  pintarDetalle();
}

/* ---------- Avisos ---------- */

function avisar(texto, tipo = "") {
  const caja = $("mensaje");
  caja.textContent = texto;
  caja.className = tipo ? "mensaje " + tipo : "mensaje";
  caja.hidden = false;
  clearTimeout(temporizadorAviso);
  temporizadorAviso = setTimeout(() => { caja.hidden = true; }, DURACION_AVISO);
}

function errorEn(id, texto) {
  const caja = $(id);
  caja.textContent = texto;
  caja.hidden = !texto;
}

/* ---------- Acciones ---------- */

function agregarAdjunto() {
  const campo = $("adjunto");
  const texto = campo.value.trim();
  if (!texto || adjuntos.includes(texto)) { campo.value = ""; return; }
  adjuntos.push(texto);
  campo.value = "";
  pintarAdjuntos();
}

function agregarIntegrante() {
  const campo = $("integrante");
  const nombre = campo.value.trim();
  if (!nombre) return;
  if (integrantes.some((p) => p.nombre === nombre)) {
    errorEn("error-entrega", "Ese integrante ya está en el equipo.");
    return;
  }
  errorEn("error-entrega", "");
  integrantes.push({ nombre, incumple: false });
  campo.value = "";
  pintarEquipo();
}

async function entregar() {
  errorEn("error-entrega", "");
  agregarAdjunto();
  const grupal = detalle.tarea.tipo === "Grupal";
  if (grupal && $("integrante").value.trim()) agregarIntegrante();
  const cuerpo = { archivos: adjuntos.filter((a) => !esEnlace(a)), enlaces: adjuntos.filter(esEnlace) };
  const numero = detalle.tarea.numero;
  try {
    let texto;
    if (grupal) {
      const respuesta = await llamarApi(`/api/tareas/${numero}/entrega-equipo`, {
        method: "POST",
        body: JSON.stringify({
          ...cuerpo,
          integrantes: integrantes.map((p) => p.nombre),
          estudiante: integrantes.length ? integrantes[0].nombre : "",
          incumplen: integrantes.filter((p) => p.incumple).map((p) => p.nombre),
        }),
      });
      texto = respuesta.mensaje;
    } else {
      texto = (await llamarApi(`/api/tareas/${numero}/entrega`, { method: "POST", body: JSON.stringify(cuerpo) })).mensaje;
    }
    avisar(texto);
    await refrescarDetalle();
  } catch (error) {
    errorEn("error-entrega", error.message);
  }
}

async function calificar() {
  errorEn("error-nota", "");
  const nota = $("nota").value.trim();
  if (nota === "" || Number.isNaN(Number(nota))) {
    errorEn("error-nota", "Escribe la nota que recibiste.");
    return;
  }
  try {
    const respuesta = await llamarApi(`/api/tareas/${detalle.tarea.numero}/calificacion`, {
      method: "POST",
      body: JSON.stringify({ nota, escala: $("escala").value, comentarios: $("comentarios").value }),
    });
    avisar(respuesta.mensaje);
    await refrescarDetalle();
  } catch (error) {
    errorEn("error-nota", error.message);
  }
}

async function guardarApunte() {
  errorEn("error-apunte", "");
  try {
    await llamarApi("/api/apuntes", {
      method: "POST",
      body: JSON.stringify({ vinculo: "tarea-" + detalle.tarea.numero, texto: $("apunte").value }),
    });
    apuntes = await llamarApi("/api/apuntes?vinculo=tarea-" + detalle.tarea.numero);
    $("apunte").value = "";
    pintarApuntes();
  } catch (error) {
    errorEn("error-apunte", error.message);
  }
}

async function borrarApunte(clave) {
  await llamarApi("/api/apuntes/" + clave, { method: "DELETE" });
  apuntes = await llamarApi("/api/apuntes?vinculo=tarea-" + detalle.tarea.numero);
  pintarApuntes();
}

/* ---------- Eventos ---------- */

function abrirDesde(evento) {
  const boton = evento.target.closest("[data-numero]");
  if (boton) abrirDetalle(Number(boton.dataset.numero), boton);
}

$("lista").addEventListener("click", abrirDesde);
$("advertencia").addEventListener("click", abrirDesde);
$("fondo").addEventListener("click", cerrarDetalle);

$("filtros").addEventListener("click", (evento) => {
  const boton = evento.target.closest(".filtro");
  if (!boton) return;
  filtro = boton.dataset.estado;
  pintarLista();
});

$("detalle").addEventListener("click", (evento) => {
  const destino = evento.target.closest("button");
  if (!destino) return;
  if (destino.hasAttribute("data-cerrar")) cerrarDetalle();
  else if (destino.id === "agregar-adjunto") agregarAdjunto();
  else if (destino.id === "agregar-integrante") agregarIntegrante();
  else if (destino.id === "entregar") entregar();
  else if (destino.id === "calificar") calificar();
  else if (destino.id === "guardar-apunte") guardarApunte();
  else if (destino.dataset.quitarAdjunto !== undefined) {
    adjuntos.splice(Number(destino.dataset.quitarAdjunto), 1);
    pintarAdjuntos();
  } else if (destino.dataset.quitarIntegrante !== undefined) {
    integrantes.splice(Number(destino.dataset.quitarIntegrante), 1);
    pintarEquipo();
  } else if (destino.dataset.borrarApunte !== undefined) borrarApunte(destino.dataset.borrarApunte);
});

$("detalle").addEventListener("change", (evento) => {
  const casilla = evento.target.closest("[data-incumple]");
  if (!casilla) return;
  integrantes[Number(casilla.dataset.incumple)].incumple = casilla.checked;
  pintarEquipo();
});

$("detalle").addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && evento.target.id === "adjunto") {
    evento.preventDefault();
    agregarAdjunto();
  } else if (evento.key === "Enter" && evento.target.id === "integrante") {
    evento.preventDefault();
    agregarIntegrante();
  } else if (evento.key === "Tab") {
    const enfocables = [...$("detalle").querySelectorAll("button, a[href], input, textarea")].filter((n) => !n.disabled);
    if (!enfocables.length) return;
    const primero = enfocables[0];
    const ultimo = enfocables[enfocables.length - 1];
    if (evento.shiftKey && document.activeElement === primero) { evento.preventDefault(); ultimo.focus(); }
    else if (!evento.shiftKey && document.activeElement === ultimo) { evento.preventDefault(); primero.focus(); }
  }
});

document.addEventListener("keydown", (evento) => {
  if (evento.key === "Escape") cerrarDetalle();
});

cargarLista().catch((error) => avisar(error.message, "error"));