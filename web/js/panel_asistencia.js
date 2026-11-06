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
  document.getElementById("historial").innerHTML = historial.map(([fecha, estado]) =>
    `<tr><td>${escapar(fecha)}</td><td><span class="etiqueta ${CLASE_ESTADO[estado] || ""}">${escapar(estado)}</span></td></tr>`).join("");
  document.getElementById("historial-vacio").hidden = historial.length > 0;
}
function mostrarAlerta(hayAlerta) {
  document.getElementById("alerta-texto").textContent = hayAlerta ? MENSAJE_ALERTA : "";
  document.getElementById("alerta").hidden = !hayAlerta;
}

document.getElementById("fecha").valueAsDate = new Date();
document.getElementById("marcar").addEventListener("click", marcarEstado);
mostrarMisClases();
