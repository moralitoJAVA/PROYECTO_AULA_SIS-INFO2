async function llamarApi(url, opciones = {}) {
  const respuesta = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opciones });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.error);
  return datos;
}

const DURACION_MENSAJE = 6000;
let temporizadorMensaje = null;

function mostrarMensaje(id, texto, tipo = "") {
  const caja = document.getElementById(id);
  caja.textContent = texto;
  caja.className = tipo ? "mensaje " + tipo : "mensaje";
  caja.hidden = !texto;
  clearTimeout(temporizadorMensaje);
  if (texto) temporizadorMensaje = setTimeout(() => { caja.hidden = true; }, DURACION_MENSAJE);
}

function escapar(texto) {
  const nodo = document.createElement("span");
  nodo.textContent = texto;
  return nodo.innerHTML.replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
