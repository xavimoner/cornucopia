
// frontend/script.js
// const BACKEND_URL = "http://backend:8000";
// Utilitzem reverse proxy, així que no cal indicar host
const BACKEND_URL = ""; // Nginx redirigeix /chat i /model al backend

document.getElementById("chat-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const pregunta = document.getElementById("pregunta").value;

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: pregunta })
    });

    if (!res.ok) throw new Error("Resposta del servidor no vàlida");

    const data = await res.json();
    document.getElementById("resposta").textContent = data.respuesta ?? "Sense resposta";

  } catch (error) {
    console.error("❌ Error al enviar la consulta:", error);
    document.getElementById("resposta").textContent = "Error al conectar con el servidor.";
  }
});

async function mostrarModeloActivo() {
  try {
    const res = await fetch(`${BACKEND_URL}/model`);
    if (!res.ok) throw new Error("Resposta del servidor no vàlida");

    const data = await res.json();
    const parrafoModelo = document.getElementById("modelo-activo");
    parrafoModelo.textContent = `Modelo activo: ${data.llm_provider} (${data.model})`;
  } catch (error) {
    console.error("❌ Error al obtener el modelo activo:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  mostrarModeloActivo();
  console.log("✅ Script carregat correctament");
});
