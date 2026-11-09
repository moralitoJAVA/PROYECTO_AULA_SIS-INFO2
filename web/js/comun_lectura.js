function fechaHoraLegible(iso) {
  if (!iso) return "";
  const f = new Date(iso.slice(0, 19));
  const dia = f.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" });
  const hora = String(f.getHours()).padStart(2, "0") + ":" + String(f.getMinutes()).padStart(2, "0");
  return `${dia}, ${hora}`;
}

function etiquetaDe(estado) {
  const clases = {
    "Respondido": "ok", "Enviada a tiempo": "ok", "Abierto": "ok",
    "Pendiente": "aviso", "Aún no abre": "info",
    "Tarde": "urgente", "Enviada tarde": "urgente", "Cerrado": "urgente",
  };
  return `<span class="etiqueta ${clases[estado] || ""}">${escapar(estado)}</span>`;
}

function enlaceDeLectura(lectura) {
  const partes = [];
  if (lectura.enlace) partes.push(`<a href="${escapar(lectura.enlace)}" target="_blank" rel="noopener noreferrer">Abrir enlace</a>`);
  if (lectura.archivo) partes.push(`<a href="${escapar(lectura.archivo)}" target="_blank" rel="noopener noreferrer">Abrir archivo</a>`);
  return partes.join(" · ");
}