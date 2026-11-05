const MS_MINUTO = 60000;
const MS_HORA = 60 * MS_MINUTO;
const MS_DIA = 24 * MS_HORA;

function fechaDe(iso) {
  return new Date(iso.slice(0, 19));
}

function restante(iso) {
  const ms = fechaDe(iso) - Date.now();
  if (ms < MS_HORA) return { cifra: Math.max(1, Math.ceil(ms / MS_MINUTO)), unidad: "min", nota: "para el plazo" };
  if (ms < MS_DIA) {
    return { cifra: Math.floor(ms / MS_HORA), unidad: "h", nota: `y ${Math.floor((ms % MS_HORA) / MS_MINUTO)} min para el plazo` };
  }
  const dias = Math.floor(ms / MS_DIA);
  return { cifra: dias, unidad: dias === 1 ? "día" : "días", nota: `y ${Math.floor((ms % MS_DIA) / MS_HORA)} h para el plazo` };
}

function formatoFecha(iso) {
  const f = fechaDe(iso);
  const dia = f.toLocaleDateString("es", { weekday: "long", day: "numeric", month: "long" });
  const hora = String(f.getHours()).padStart(2, "0") + ":" + String(f.getMinutes()).padStart(2, "0");
  return `${dia}, ${hora}`;
}

function pintarProxima(datos) {
  const caja = document.getElementById("proxima");
  const pendientes = datos.tareas.filter((t) => t.estado === "Pendiente" && fechaDe(t.fecha_limite) > Date.now());
  caja.classList.remove("cargando", "urgente", "libre");
  if (!pendientes.length) {
    caja.classList.add("libre");
    caja.innerHTML = `<div class="proxima-texto"><h2>No tienes entregas pendientes</h2>` +
      `<p>Cuando haya una tarea nueva por entregar, la verás aquí.</p></div>` +
      `<a class="proxima-boton" href="/tareas.html">Ver mis tareas</a>`;
    return;
  }
  const siguiente = pendientes[0];
  const r = restante(siguiente.fecha_limite);
  if (datos.por_vencer.includes(siguiente.numero)) caja.classList.add("urgente");
  const otras = pendientes.length - 1;
  caja.innerHTML = `<div class="proxima-reloj"><span class="proxima-cifra">${r.cifra}</span><span class="proxima-unidad">${r.unidad}</span></div>` +
    `<div class="proxima-texto"><h2>${escapar(siguiente.titulo)}</h2>` +
    `<p>${escapar(r.nota)}. Límite: ${escapar(formatoFecha(siguiente.fecha_limite))}` +
    `${otras ? `. Tienes ${otras} ${otras === 1 ? "tarea pendiente más" : "tareas pendientes más"}` : ""}.</p></div>` +
    `<a class="proxima-boton" href="/tareas.html">Entregar tarea</a>`;
}

llamarApi("/api/tareas")
  .then(pintarProxima)
  .catch(() => {
    const caja = document.getElementById("proxima");
    caja.className = "proxima cargando";
    caja.innerHTML = "<div>No se pudo cargar la próxima entrega. Recarga la página.</div>";
  });