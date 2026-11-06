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
}

async function marcarEstado() {
  try {
    const { materia, fecha } = elegirClase();
    const estado = document.getElementById("estado").value;
    const respuesta = await llamarApi("/api/asistencia", { method: "POST", body: JSON.stringify({ materia, fecha, estado }) });
    mostrarMensaje("mensaje", "Asistencia guardada. " + respuesta.resumen);
    await mostrarMisClases();
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

function mostrarResumen(resumen) { mostrarMensaje("mensaje", "Resumen: " + resumen); }
function mostrarHistorial(historial) {
  document.getElementById("historial").innerHTML = historial.map(([fecha, estado]) => `<tr><td>${escapar(fecha)}</td><td>${escapar(estado)}</td></tr>`).join("");
}
function mostrarAlerta(hayAlerta) {
  const caja = document.getElementById("alerta");
  caja.textContent = hayAlerta ? MENSAJE_ALERTA : "";
  caja.hidden = !hayAlerta;
}

const seRestauroFormulario = restaurarFormulario();
for (const id of ["materia", "fecha", "estado"]) {
  document.getElementById(id).addEventListener("change", guardarFormulario);
}
document.getElementById("materia").addEventListener("input", guardarFormulario);
document.getElementById("marcar").addEventListener("click", marcarEstado);
mostrarMisClases().then(() => {
  if (seRestauroFormulario) mostrarMensaje("mensaje", "Se restauraron tus preferencias de asistencia.");
}).catch((error) => mostrarMensaje("mensaje", error.message, "error"));
