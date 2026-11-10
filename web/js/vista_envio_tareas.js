const campoMateria = document.getElementById("materia");
const salidaDocente = document.getElementById("docente");
const estado = document.getElementById("estado");

async function mostrarDocente() {
  const materia = campoMateria.value.trim();
  if (!materia) return;
  try {
    const datos = await llamarApi(`/api/materias/${encodeURIComponent(materia)}/docente`);
    salidaDocente.textContent = datos.correo_docente;
  } catch (error) {
    salidaDocente.textContent = error.message;
  }
}

function leerArchivo(archivo) {
  return new Promise((resolver) => {
    const lector = new FileReader();
    lector.onload = () => resolver({ nombre: archivo.name, contenido: lector.result.split(",")[1] });
    lector.readAsDataURL(archivo);
  });
}

async function enviarTarea(evento) {
  evento.preventDefault();
  try {
    const archivos = document.getElementById("adjuntos").files;
    if (!archivos.length) throw new Error("Debes adjuntar al menos un archivo");
    const adjuntos = await Promise.all([...archivos].map(leerArchivo));
    const materia = campoMateria.value.trim();
    const tarea = document.getElementById("tarea").value.trim();
    const datos = await llamarApi(
      `/api/materias/${encodeURIComponent(materia)}/tareas/${encodeURIComponent(tarea)}/envio`,
      {
        method: "POST",
        body: JSON.stringify({
          estudiante: document.getElementById("estudiante").value,
          correo_estudiante: document.getElementById("correo_estudiante").value,
          fecha_limite: document.getElementById("fecha_limite").value,
          adjuntos,
        }),
      },
    );
    estado.innerHTML = `Estado de la tarea: <strong>${escapar(datos.estado)}</strong> (${escapar(datos.puntualidad)})`;
    mostrarMensaje("mensaje", datos.mensaje, "exito");
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

async function guardarDocente(evento) {
  evento.preventDefault();
  try {
    const datos = await llamarApi("/api/materias", {
      method: "POST",
      body: JSON.stringify({
        materia: document.getElementById("materia-docente").value,
        correo_docente: document.getElementById("correo-docente").value,
      }),
    });
    campoMateria.value = datos.materia;
    await mostrarDocente();
    mostrarMensaje("mensaje", `Correo del docente guardado para ${datos.materia}`, "exito");
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

campoMateria.addEventListener("blur", mostrarDocente);
document.getElementById("formulario-docente").addEventListener("submit", guardarDocente);
document.getElementById("formulario").addEventListener("submit", enviarTarea);
mostrarDocente();
