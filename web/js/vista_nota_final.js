const COMPONENTES = ["asistencia", "tareas", "examenes", "proyecto"];
const TEXTO_PENDIENTE = "pendiente";
 
async function mostrarPesos() {
  const pesos = await llamarApi("/api/pesos");
  COMPONENTES.forEach((c) => {
    document.getElementById("peso-" + c).value = pesos[c];
  });
}
 
async function guardarPesos() {
  try {
    const pesos = {};
    COMPONENTES.forEach((c) => {
      pesos[c] = document.getElementById("peso-" + c).value || "0";
    });
    await llamarApi("/api/pesos", { method: "PUT", body: JSON.stringify(pesos) });
    mostrarMensaje("mensaje", "Pesos guardados");
    await mostrarDesglose();
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}
 
function valorOPendiente(valor, sufijo = "") {
  return valor === null ? TEXTO_PENDIENTE : escapar(valor) + sufijo;
}
 
async function mostrarDesglose() {
  const datos = await llamarApi("/api/nota-final");
  document.getElementById("nota-final").textContent = valorOPendiente(datos.nota_final);
  document.getElementById("parcial").textContent = datos.parcial ? "(parcial: hay componentes pendientes)" : "";
  document.getElementById("desglose").innerHTML = COMPONENTES.map((c) => {
    const d = datos.componentes[c];
    return `<tr><td>${c}</td><td>${escapar(d.peso)}%</td><td>${valorOPendiente(d.nota)}</td>
      <td>${valorOPendiente(d.aporte)}</td><td>${d.penalizacion === null ? "-" : escapar(d.penalizacion)}</td></tr>`;
  }).join("");
}
 
document.getElementById("guardar").addEventListener("click", guardarPesos);
mostrarPesos();
mostrarDesglose();
