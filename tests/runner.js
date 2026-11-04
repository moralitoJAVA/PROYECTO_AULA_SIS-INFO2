import { ejecutarPruebas } from "./core/baseDatos.test.js";

const salida = document.querySelector("#resultado");
const resultados = ejecutarPruebas();
salida.innerHTML = resultados.map(({ nombre, error }) => `<p>${error ? "❌" : "✅"} ${nombre}${error ? `: ${error.message}` : ""}</p>`).join("");
