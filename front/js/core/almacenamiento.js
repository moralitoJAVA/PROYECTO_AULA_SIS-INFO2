

/** Guarda datos serializables en el almacenamiento local del navegador. */
export function guardar(clave, valor) {
  localStorage.setItem(clave, JSON.stringify(valor));
}

/** Devuelve el valor almacenado o el valor inicial cuando no existe. */
export function obtener(clave, valorInicial = null) {
  const contenido = localStorage.getItem(clave);
  if (contenido === null) return valorInicial;
  try { return JSON.parse(contenido); } catch { return valorInicial; }
}

/** Elimina únicamente las claves que pertenecen al proyecto. */
export function limpiarProyecto(prefijo = "sis-info2:") {
  Object.keys(localStorage).filter((clave) => clave.startsWith(prefijo)).forEach((clave) => localStorage.removeItem(clave));
}
