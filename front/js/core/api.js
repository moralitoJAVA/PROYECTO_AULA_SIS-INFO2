/** Realiza una solicitud a la API del proyecto y devuelve su respuesta JSON. */
export async function solicitar(ruta, opciones = {}) {
  const respuesta = await fetch(`/api/${ruta}`, {
    headers: { "Content-Type": "application/json", ...opciones.headers },
    ...opciones,
  });

  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.error || "No fue posible procesar la solicitud.");
  return datos;
}
