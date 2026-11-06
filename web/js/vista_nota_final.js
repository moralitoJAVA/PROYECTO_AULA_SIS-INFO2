const COMPONENTES = [&quot;asistencia&quot;, &quot;tareas&quot;, &quot;examenes&quot;, &quot;proyecto&quot;];
const TEXTO_PENDIENTE = &quot;pendiente&quot;;
const NOMBRES = { asistencia: &quot;Asistencia&quot;, tareas: &quot;Tareas&quot;, examenes: &quot;Exámenes&quot;, proyecto: &quot;Proyecto en
equipo&quot; };
async function mostrarPesos() {
const pesos = await llamarApi(&quot;/api/pesos&quot;);
COMPONENTES.forEach((c) =&gt; {
document.getElementById(&quot;peso-&quot; + c).value = pesos[c];
});
}
async function guardarPesos() {
try {
const pesos = {};
COMPONENTES.forEach((c) =&gt; {
pesos[c] = document.getElementById(&quot;peso-&quot; + c).value || &quot;0&quot;;
});
await llamarApi(&quot;/api/pesos&quot;, { method: &quot;PUT&quot;, body: JSON.stringify(pesos) });
mostrarMensaje(&quot;mensaje&quot;, &quot;Pesos guardados&quot;);
await mostrarDesglose();
} catch (error) {
mostrarMensaje(&quot;mensaje&quot;, error.message, &quot;error&quot;);
}
}
function valorOPendiente(valor, sufijo = &quot;&quot;) {
return valor === null ? TEXTO_PENDIENTE : escapar(valor) + sufijo;
}
async function mostrarDesglose() {
const datos = await llamarApi(&quot;/api/nota-final&quot;);
document.getElementById(&quot;nota-final&quot;).textContent = valorOPendiente(datos.nota_final);
document.getElementById(&quot;parcial&quot;).textContent = datos.parcial ? &quot;(parcial: hay componentes pendientes)&quot; : &quot;&quot;;
document.getElementById(&quot;desglose&quot;).innerHTML = COMPONENTES.map((c) =&gt; {
const d = datos.componentes[c];
return `&lt;tr&gt;&lt;td&gt;${NOMBRES[c]}&lt;/td&gt;&lt;td class=&quot;num&quot;&gt;${escapar(d.peso)}%&lt;/td&gt;&lt;td
class=&quot;num&quot;&gt;${valorOPendiente(d.nota)}&lt;/td&gt;
&lt;td class=&quot;num&quot;&gt;${valorOPendiente(d.aporte)}&lt;/td&gt;&lt;td class=&quot;num&quot;&gt;${d.penalizacion === null ? &quot;-&quot; :
escapar(d.penalizacion)}&lt;/td&gt;&lt;/tr&gt;`;
}).join(&quot;&quot;);
}
document.getElementById(&quot;guardar&quot;).addEventListener(&quot;click&quot;, guardarPesos);
mostrarPesos();
mostrarDesglose();
