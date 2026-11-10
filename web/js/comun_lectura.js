function dosDigitos(n) {
  return String(n).padStart(2, "0");
}

function fechaHoraLegible(iso) {
  if (!iso) return "";
  const f = new Date(iso.slice(0, 19));
  const dia = f.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" });
  return `${dia}, ${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}`;
}

/* Fecha y hora exactas (con segundos), como figuran en el PDF entregado. */
function fechaHoraExacta(iso) {
  if (!iso) return "";
  const f = new Date(iso.slice(0, 19));
  return `${dosDigitos(f.getDate())}/${dosDigitos(f.getMonth() + 1)}/${f.getFullYear()} ` +
    `${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}:${dosDigitos(f.getSeconds())}`;
}

function etiquetaDe(estado) {
  const clases = {
    "Respondido": "ok", "A tiempo": "ok", "Dentro del plazo": "ok",
    "Pendiente": "aviso", "Antes de la clase": "info",
    "Tarde": "urgente", "Plazo vencido": "urgente",
  };
  return `<span class="etiqueta ${clases[estado] || ""}">${escapar(estado)}</span>`;
}

function enlaceDeLectura(lectura) {
  const partes = [];
  if (lectura.enlace) partes.push(`<a href="${escapar(lectura.enlace)}" target="_blank" rel="noopener noreferrer">Abrir enlace</a>`);
  if (lectura.archivo) partes.push(`<a href="${escapar(lectura.archivo)}" target="_blank" rel="noopener noreferrer">Abrir archivo</a>`);
  return partes.join(" · ");
}