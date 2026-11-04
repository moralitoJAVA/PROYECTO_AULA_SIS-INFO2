const MENSAJE_ALERTA = "Tu asistencia está por debajo del mínimo configurado (80%).";

function elegirClase() {
  return { materia: document.getElementById("materia").value, fecha: document.getElementById("fecha").value };
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

document.getElementById("marcar").addEventListener("click", marcarEstado);
mostrarMisClases();
