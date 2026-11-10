/* HU1: registrar la hora de ingreso y mostrar si es "Puntual" o "Debe fruta". */
const CLASE_SANCION = { "Puntual": "ok", "Debe fruta": "urgente" };

function fechaLegible(iso) {
  const [anio, mes, dia] = iso.split("-");
  return `${dia}/${mes}/${anio}`;
}

function pintarIngresos(datos) {
  const filas = datos.ingresos.map((i) =>
    `<tr><td>${escapar(fechaLegible(i.fecha))}</td><td>${escapar(i.hora_ingreso)}</td>` +
    `<td><span class="etiqueta ${CLASE_SANCION[i.estado] || ""}">${escapar(i.estado)}</span></td></tr>`);
  document.getElementById("ingreso-historial").innerHTML = filas.join("");
  document.getElementById("ingreso-vacio").hidden = datos.ingresos.length > 0;

  const pendiente = datos.fruta_pendiente;
  document.getElementById("fruta-aviso-texto").textContent = pendiente
    ? `Debes llevar una fruta a la clase del ${fechaLegible(pendiente.fruta_para)} (llegaste a las ${pendiente.hora_ingreso} el ${fechaLegible(pendiente.fecha)}).`
    : "";
  document.getElementById("fruta-aviso").hidden = !pendiente;
}

async function cargarIngresos() {
  const materia = document.getElementById("materia").value;
  pintarIngresos(await llamarApi("/api/asistencia/ingresos?materia=" + encodeURIComponent(materia)));
}

async function registrarIngreso() {
  const resultado = document.getElementById("ingreso-resultado");
  try {
    const cuerpo = { materia: document.getElementById("materia").value };
    const fecha = document.getElementById("ingreso-fecha").value;
    if (fecha) cuerpo.fecha = fecha.length === 16 ? fecha + ":00" : fecha;
    const ingreso = await llamarApi("/api/asistencia/ingreso", { method: "POST", body: JSON.stringify(cuerpo) });
    resultado.textContent = (ingreso.debe_fruta ? "🍎 " : "✅ ") + ingreso.mensaje;
    await cargarIngresos();
    window.dispatchEvent(new CustomEvent("asistencia-actualizada"));
    mostrarMensaje("mensaje", ingreso.debe_fruta ? "Debe fruta" : "Puntual", ingreso.debe_fruta ? "error" : "");
  } catch (error) {
    resultado.textContent = "";
    mostrarMensaje("mensaje", error.message, "error");
  }
}

document.getElementById("ingreso-registrar").addEventListener("click", registrarIngreso);
document.getElementById("materia").addEventListener("change", () => cargarIngresos().catch(() => {}));
cargarIngresos().catch((error) => mostrarMensaje("mensaje", error.message, "error"));