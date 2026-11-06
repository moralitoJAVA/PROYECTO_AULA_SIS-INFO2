const listaCriterios = document.getElementById("criterios");

function actualizarTotal() {
  const total = [...listaCriterios.querySelectorAll(".puntaje")]
    .reduce((suma, campo) => suma + (Number(campo.value) || 0), 0);
  document.getElementById("total").textContent = total;
}

function agregarCriterio(nombre = "", puntaje = "") {
  const item = document.createElement("li");
  item.className = "criterio";
  item.innerHTML = `<input class="nombre-criterio" required aria-label="Nombre del criterio" placeholder="Criterio" value="${escapar(nombre)}">` +
    `<input class="puntaje" required type="number" min="0.01" step="0.01" aria-label="Puntaje" placeholder="Puntos" value="${escapar(String(puntaje))}">` +
    '<button type="button" class="boton secundario quitar-criterio" aria-label="Quitar criterio">Quitar</button>';
  item.querySelector(".puntaje").addEventListener("input", actualizarTotal);
  item.querySelector(".quitar-criterio").addEventListener("click", () => { item.remove(); actualizarTotal(); });
  listaCriterios.append(item);
  actualizarTotal();
}

function alternarTamano() {
  const esGrupal = document.getElementById("tipo").value === "Grupal";
  document.getElementById("campo-tamano").hidden = !esGrupal;
  document.getElementById("tamano_equipo").required = esGrupal;
}

async function registrarTarea(evento) {
  evento.preventDefault();
  try {
    const tipo = document.getElementById("tipo").value;
    const datos = {
      titulo: document.getElementById("titulo").value,
      instrucciones: document.getElementById("instrucciones").value,
      fecha_limite: document.getElementById("fecha_limite").value,
      tipo,
      ruta_adjunto: document.getElementById("ruta_adjunto").value,
      criterios: [...listaCriterios.querySelectorAll(".criterio")].map((item) => ({
        nombre: item.querySelector(".nombre-criterio").value,
        puntaje: item.querySelector(".puntaje").value,
      })),
    };
    if (tipo === "Grupal") datos.tamano_equipo = Number(document.getElementById("tamano_equipo").value);
    const respuesta = await llamarApi("/api/tareas", { method: "POST", body: JSON.stringify(datos) });
    mostrarMensaje("mensaje", `Tarea ${respuesta.codigo} registrada`);
    document.getElementById("formulario").reset();
    listaCriterios.replaceChildren();
    agregarCriterio();
    alternarTamano();
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

document.getElementById("tipo").addEventListener("change", alternarTamano);
document.getElementById("agregar-criterio").addEventListener("click", () => agregarCriterio());
document.getElementById("formulario").addEventListener("submit", registrarTarea);
agregarCriterio();
alternarTamano();
