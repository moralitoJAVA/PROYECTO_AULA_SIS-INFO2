import { guardar, obtener } from "/front/js/core/almacenamiento.js";

const MENSAJE_ALERTA = "Tu asistencia está por debajo del mínimo configurado (80%).";
const CLAVE_FORMULARIO = "sis-info2:asistencia:formulario";

function elegirClase() {
  return { materia: document.getElementById("materia").value, fecha: document.getElementById("fecha").value };
}

function guardarFormulario() {
  guardar(CLAVE_FORMULARIO, { ...elegirClase(), estado: document.getElementById("estado").value });
}

function restaurarFormulario() {
  const formulario = obtener(CLAVE_FORMULARIO);
  if (!formulario) return false;

  for (const campo of ["materia", "fecha", "estado"]) {
    if (typeof formulario[campo] === "string") document.getElementById(campo).value = formulario[campo];
  }
  return true;
}

async function mostrarMisClases() {
  const { materia } = elegirClase();
  const panel = await llamarApi("/api/asistencia/panel?materia=" + encodeURIComponent(materia));
  mostrarResumen(panel.resumen);
  mostrarHistorial(panel.historial);
  mostrarAlerta(panel.alerta);
  document.getElementById("porcentaje").textContent = panel.porcentaje === null ? "pendiente" : panel.porcentaje + "%";
  document.getElementById("metrica").className = "metrica" + (panel.porcentaje === null ? "" : panel.alerta ? " urgente" : " ok");
}

async function marcarEstado() {
  try {
    const { materia, fecha } = elegirClase();
    const estado = document.getElementById("estado").value;
    await llamarApi("/api/asistencia", { method: "POST", body: JSON.stringify({ materia, fecha, estado }) });
    await mostrarMisClases();
    mostrarMensaje("mensaje", "Asistencia guardada");
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

function mostrarResumen(resumen) { document.getElementById("resumen").textContent = resumen; }
const CLASE_ESTADO = { Presente: "ok", Atraso: "aviso", Ausente: "urgente", Licencia: "info" };
function mostrarHistorial(historial) {
  document.getElementById("historial").innerHTML = historial.map(([fecha, estado]) => {
    const fruta = estado === "Atraso"
      ? ` <span class="etiqueta urgente" title="Debes llevar una fruta a la siguiente clase">Debe fruta</span>` : "";
    return `<tr><td>${escapar(fecha)}</td><td><span class="etiqueta ${CLASE_ESTADO[estado] || ""}">${escapar(estado)}</span>${fruta}</td></tr>`;
  }).join("");
  document.getElementById("historial-vacio").hidden = historial.length > 0;
}
function mostrarAlerta(hayAlerta) {
  document.getElementById("alerta-texto").textContent = hayAlerta ? MENSAJE_ALERTA : "";
  document.getElementById("alerta").hidden = !hayAlerta;
}

const seRestauroFormulario = restaurarFormulario();
if (!document.getElementById("fecha").value) document.getElementById("fecha").valueAsDate = new Date();
for (const id of ["materia", "fecha", "estado"]) {
  document.getElementById(id).addEventListener("change", guardarFormulario);
}
document.getElementById("materia").addEventListener("input", guardarFormulario);
document.getElementById("marcar").addEventListener("click", marcarEstado);
window.addEventListener("asistencia-actualizada", () => mostrarMisClases().catch((error) => mostrarMensaje("mensaje", error.message, "error")));

mostrarMisClases().then(() => {
  if (seRestauroFormulario) mostrarMensaje("mensaje", "Se restauraron tus preferencias de asistencia.");
}).catch((error) => mostrarMensaje("mensaje", error.message, "error"));