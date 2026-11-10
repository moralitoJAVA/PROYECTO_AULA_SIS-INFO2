const CLASE_ESTADO = {
  "Pendiente": "info",
  "No revisada": "urgente",
  "Pendiente de revisión": "aviso",
  "Revisada": "ok",
  "Reentrega": "aviso",
};
const CLASE_PUNTUALIDAD = { "Puntual": "ok", "Tardío": "aviso", "Ausente": "urgente", "Licencia": "info", "Sin registrar": "" };
const lista = document.getElementById("lista");

function dosDigitos(n) {
  return String(n).padStart(2, "0");
}

function formatoExacto(iso) {
  const f = new Date(iso.slice(0, 19));
  return `${dosDigitos(f.getDate())}/${dosDigitos(f.getMonth() + 1)}/${f.getFullYear()} ` +
    `${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}:${dosDigitos(f.getSeconds())}`;
}

function dato(titulo, valor) {
  return `<div><dt>${escapar(titulo)}</dt><dd>${valor}</dd></div>`;
}

function accionDocente(r) {
  if (!r.puede_revisarse) return "";
  return `<form class="revision-accion" data-revisar="${r.numero}">
    <h3>Registrar revisión del docente</h3>
    <div class="opciones">
      <label><input type="radio" name="errores-${r.numero}" value="no" checked> Sin errores</label>
      <label><input type="radio" name="errores-${r.numero}" value="si"> Con errores</label>
    </div>
    <label for="obs-${r.numero}">Observaciones</label>
    <textarea id="obs-${r.numero}" name="observaciones" rows="3" maxlength="1000"></textarea>
    <button class="boton primario grande" type="submit">Registrar revisión</button>
  </form>`;
}

function accionReentrega(r) {
  if (r.reentrega_habilitada) {
    return `<form class="revision-accion" data-reentrega="${r.numero}">
      <h3>${r.estado === "Reentrega" ? "Reentrega" : "Reenviar otra versión"}</h3>
      <p class="ayuda">Adjunta el PDF corregido. Reemplaza tu entrega anterior y la tarea queda pendiente de revisión.
        Puedes reenviar las veces que necesites hasta ${escapar(formatoExacto(r.plazo_reentrega))}, la siguiente clase donde se revisa de nuevo.</p>
      <label for="pdf-${r.numero}">Archivo PDF</label>
      <input id="pdf-${r.numero}" name="pdf" type="file" accept="application/pdf,.pdf" required>
      <button class="boton primario grande" type="submit">Reentregar</button>
    </form>`;
  }
  return r.mensaje_reentrega ? `<p class="revision-aviso info">${escapar(r.mensaje_reentrega)}</p>` : "";
}

function tarjeta(r) {
  const entrega = r.fecha_entrega ? formatoExacto(r.fecha_entrega) : "Sin entrega";
  const entregaEtiqueta = r.a_tiempo === null ? "" :
    ` <span class="etiqueta ${r.a_tiempo ? "ok" : "urgente"}">${r.a_tiempo ? "A tiempo" : "Tarde"}</span>`;
  const motivo = r.motivo ? `<p class="revision-aviso" role="alert">${escapar(r.motivo)}</p>` : "";
  const observaciones = r.observaciones
    ? `<p class="revision-obs"><strong>Observaciones del docente:</strong> ${escapar(r.observaciones)}</p>` : "";
  const archivos = r.archivos.length ? r.archivos.map(escapar).join(", ") : "—";
  return `<li class="tarjeta" data-numero="${r.numero}">
    <div class="revision-cabecera">
      <h2>${escapar(r.titulo)}</h2>
      <span class="etiqueta ${CLASE_ESTADO[r.estado] || ""}">${escapar(r.estado)}</span>
    </div>
    <dl class="revision-datos">
      ${dato("Fecha límite", escapar(formatoExacto(r.fecha_limite)))}
      ${dato("Fecha y hora de entrega", escapar(entrega) + entregaEtiqueta)}
      ${dato("Puntualidad", `<span class="etiqueta ${CLASE_PUNTUALIDAD[r.puntualidad] || ""}">${escapar(r.puntualidad)}</span>`)}
      ${dato("Entrega vigente", escapar(archivos) + (r.version ? ` (versión ${r.version})` : ""))}
    </dl>
    ${motivo}${observaciones}${accionDocente(r)}${accionReentrega(r)}
    ${r.version ? `<button class="boton secundario" type="button" data-historial="${r.numero}">Ver historial de versiones</button>` : ""}
    <ul class="revision-historial" data-lista-historial="${r.numero}" hidden></ul>
  </li>`;
}

async function cargar() {
  const datos = await llamarApi("/api/revision-tareas");
  lista.innerHTML = datos.revisiones.map(tarjeta).join("");
  document.getElementById("vacio").hidden = datos.revisiones.length > 0;
}

async function registrarRevision(formulario) {
  const numero = formulario.dataset.revisar;
  const conErrores = formulario.elements["errores-" + numero].value === "si";
  const observaciones = formulario.elements.observaciones.value;
  await llamarApi(`/api/revision-tareas/${numero}/revision`, {
    method: "POST", body: JSON.stringify({ con_errores: conErrores, observaciones }),
  });
  await cargar();
  mostrarMensaje("mensaje", "Revisión registrada");
}

async function enviarReentrega(formulario) {
  const numero = formulario.dataset.reentrega;
  const archivo = formulario.elements.pdf.files[0];
  if (!archivo) throw new Error("Debes adjuntar un archivo PDF para la reentrega");
  const datos = await llamarApi(`/api/revision-tareas/${numero}/reentrega`, {
    method: "POST", body: JSON.stringify({ archivos: [archivo.name] }),
  });
  await cargar();
  mostrarMensaje("mensaje", datos.mensaje);
}

async function mostrarHistorial(numero) {
  const caja = document.querySelector(`[data-lista-historial="${numero}"]`);
  if (!caja.hidden) { caja.hidden = true; return; }
  const datos = await llamarApi(`/api/revision-tareas/${numero}/historial`);
  caja.innerHTML = datos.versiones.map((v) => {
    const revision = v.con_errores === null ? "" : v.con_errores
      ? ` — revisada con errores: ${escapar(v.observaciones || "")}` : " — revisada sin errores";
    return `<li>Versión ${v.version}${v.vigente ? " (vigente)" : ""}: ${v.archivos.map(escapar).join(", ")}, ` +
      `entregada ${escapar(formatoExacto(v.fecha_hora_entrega))}${revision}</li>`;
  }).join("");
  caja.hidden = false;
}

function atender(evento, accion) {
  evento.preventDefault();
  accion().catch((error) => mostrarMensaje("mensaje", error.message, "error"));
}

lista.addEventListener("submit", (evento) => {
  const formulario = evento.target;
  if (formulario.dataset.revisar) atender(evento, () => registrarRevision(formulario));
  if (formulario.dataset.reentrega) atender(evento, () => enviarReentrega(formulario));
});

lista.addEventListener("click", (evento) => {
  const boton = evento.target.closest("[data-historial]");
  if (boton) atender(evento, () => mostrarHistorial(boton.dataset.historial));
});

cargar().catch((error) => mostrarMensaje("mensaje", error.message, "error"));
