const SEPARADOR = ",";
let tareaAbierta = null;

function lista(id) {
  return document.getElementById(id).value.split(SEPARADOR).map((x) => x.trim()).filter((x) => x !== "");
}

function esEnlace(texto) {
  return texto.startsWith("http://") || texto.startsWith("https://");
}

async function mostrarPanel() {
  const filtro = document.getElementById("filtro").value;
  const datos = await llamarApi("/api/tareas" + (filtro ? "?estado=" + filtro : ""));
  document.getElementById("lista").innerHTML = datos.tareas
    .map((t) => `<tr><td>${t.numero}</td><td>${escapar(t.titulo)}</td><td>${escapar(t.tipo)}</td>
      <td>${escapar(t.fecha_limite.replace("T", " "))}</td><td>${escapar(t.estado)}</td>
      <td>${t.nota === null ? "" : escapar(t.nota)}</td>
      <td>${t.nota === null ? "" : escapar(t.descuento) + "%"}</td>
      <td>${t.nota_final === null ? "" : escapar(t.nota_final)}</td>
      <td><button data-numero="${t.numero}">Abrir</button></td></tr>`)
    .join("");
  document.querySelectorAll("#lista button").forEach((b) =>
    b.addEventListener("click", () => abrirDetalle(Number(b.dataset.numero))));
  mostrarAdvertencia(datos.por_vencer);
}

function mostrarAdvertencia(porVencer) {
  const caja = document.getElementById("advertencia");
  caja.textContent = porVencer.length ? "Vence en menos de 24 horas: tarea(s) " + porVencer.join(", ") : "";
  caja.hidden = porVencer.length === 0;
}

async function abrirDetalle(numero) {
  const datos = await llamarApi("/api/tareas/" + numero);
  tareaAbierta = datos.tarea;
  document.getElementById("detalle").hidden = false;
  document.getElementById("detalle-titulo").textContent = `${datos.tarea.codigo} · ${datos.tarea.titulo}`;
  document.getElementById("detalle-texto").textContent = datos.tarea.instrucciones;
  document.getElementById("detalle-maximo").textContent = datos.puntaje_maximo;
  document.getElementById("bloque-equipo").hidden = datos.tarea.tipo !== "Grupal";
  mostrarAdjunto(datos.tarea.ruta_adjunto);
  mostrarResumen(datos);
  await mostrarApuntes();
}

function mostrarAdjunto(ruta) {
  const contenedor = document.getElementById("detalle-adjunto");
  contenedor.textContent = "";
  if (!ruta) return;
  if (esEnlace(ruta) || ruta.startsWith("/")) {
    const enlace = document.createElement("a");
    enlace.href = ruta;
    enlace.textContent = "Descargar " + ruta.split("/").pop();
    enlace.setAttribute("download", "");
    contenedor.appendChild(enlace);
  } else {
    contenedor.textContent = ruta;
  }
}

function mostrarResumen(datos) {
  const entrega = datos.entrega;
  const confirmacion = document.getElementById("detalle-entrega");
  const entregada = entrega.estado !== "Pendiente";
  confirmacion.hidden = !entregada;
  if (entregada) {
    const fecha = entrega.fecha_hora_entrega.replace("T", " ");
    confirmacion.textContent = `Estado: ${entrega.estado}. Entregada el ${fecha}. ` +
      `Archivos: ${[...entrega.archivos, ...entrega.enlaces].join(", ")}` +
      (datos.equipo ? `. Equipo: ${datos.equipo.integrantes.join(", ")}` : "");
  }
  const penalizacion = document.getElementById("detalle-penalizacion");
  penalizacion.hidden = !datos.penalizacion;
  penalizacion.textContent = datos.penalizacion ? "Penalización: " + datos.penalizacion.motivo : "";
  const calificacion = document.getElementById("detalle-calificacion");
  const calificada = entrega.estado === "Calificada";
  calificacion.hidden = !calificada;
  if (calificada) {
    calificacion.textContent = `Nota: ${entrega.nota} / ${entrega.puntaje_maximo} (escala ${entrega.escala}). ` +
      `Comentarios: ${entrega.comentarios || "sin comentarios"}`;
  }
}

async function subirEntrega() {
  try {
    const items = lista("archivos");
    const cuerpo = { archivos: items.filter((x) => !esEnlace(x)), enlaces: items.filter(esEnlace) };
    let respuesta;
    if (tareaAbierta.tipo === "Grupal") {
      const integrantes = lista("integrantes");
      respuesta = await llamarApi(`/api/tareas/${tareaAbierta.numero}/entrega-equipo`, {
        method: "POST",
        body: JSON.stringify({ ...cuerpo, integrantes, estudiante: integrantes[0], incumplen: lista("incumplen") }),
      });
      const motivo = respuesta.motivo ? " " + respuesta.motivo : "";
      mostrarMensaje("mensaje", respuesta.mensaje + motivo);
    } else {
      respuesta = await llamarApi(`/api/tareas/${tareaAbierta.numero}/entrega`, { method: "POST", body: JSON.stringify(cuerpo) });
      mostrarMensaje("mensaje", respuesta.mensaje);
    }
    await mostrarPanel();
    await abrirDetalle(tareaAbierta.numero);
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

async function guardarCalificacion() {
  try {
    const cuerpo = {
      nota: document.getElementById("nota").value,
      escala: document.getElementById("escala").value,
      comentarios: document.getElementById("comentarios").value,
    };
    const r = await llamarApi(`/api/tareas/${tareaAbierta.numero}/calificacion`, { method: "POST", body: JSON.stringify(cuerpo) });
    mostrarMensaje("mensaje", r.mensaje);
    await mostrarPanel();
    await abrirDetalle(tareaAbierta.numero);
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

async function mostrarApuntes() {
  const vinculo = "tarea-" + tareaAbierta.numero;
  const apuntes = await llamarApi("/api/apuntes?vinculo=" + vinculo);
  document.getElementById("apuntes").innerHTML = apuntes
    .map((a) => `<li>${escapar(a.texto)} <button data-clave="${a.clave}">Borrar</button></li>`)
    .join("");
  document.querySelectorAll("#apuntes button").forEach((b) =>
    b.addEventListener("click", async () => {
      await llamarApi("/api/apuntes/" + b.dataset.clave, { method: "DELETE" });
      await mostrarApuntes();
    }));
}

async function guardarApunte() {
  try {
    const texto = document.getElementById("apunte").value;
    await llamarApi("/api/apuntes", { method: "POST", body: JSON.stringify({ vinculo: "tarea-" + tareaAbierta.numero, texto }) });
    document.getElementById("apunte").value = "";
    await mostrarApuntes();
  } catch (error) {
    mostrarMensaje("mensaje", error.message, "error");
  }
}

function mostrarHistorial() {
  document.getElementById("filtro").value = "";
  return mostrarPanel();
}

document.getElementById("filtro").addEventListener("change", mostrarPanel);
document.getElementById("entregar").addEventListener("click", subirEntrega);
document.getElementById("calificar").addEventListener("click", guardarCalificacion);
document.getElementById("guardar-apunte").addEventListener("click", guardarApunte);
mostrarPanel();