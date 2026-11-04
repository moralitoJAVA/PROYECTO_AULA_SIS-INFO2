import { solicitar } from "./core/api.js";

// Registrar aquí los módulos de Historias de Usuario cuando sean implementados.
// Ejemplo: { id: "HU-01", titulo: "Registrar tarea", renderizar: renderizarHU01 }
const historiasUsuario = [];
const menu = document.querySelector("#menu-historias");
const mensajeVacio = document.querySelector("#mensaje-vacio");
const contenido = document.querySelector("#contenido-hu");
const botonLimpiar = document.querySelector("#boton-limpiar");

function mostrarHistoria(historia) {
  contenido.replaceChildren();
  historia.renderizar(contenido);
}

function construirMenu() {
  mensajeVacio.hidden = historiasUsuario.length > 0;
  historiasUsuario.forEach((historia) => {
    const boton = document.createElement("button");
    boton.className = "boton";
    boton.type = "button";
    boton.textContent = `${historia.id}: ${historia.titulo}`;
    boton.addEventListener("click", () => mostrarHistoria(historia));
    menu.append(boton);
  });
}

botonLimpiar.addEventListener("click", async () => {
  try {
    const estado = await solicitar("estado");
    window.alert(`Conexión exitosa. Base de datos: ${estado.base_datos}.`);
  } catch (error) {
    window.alert(`No se pudo conectar al servidor: ${error.message}`);
  }
});
construirMenu();
