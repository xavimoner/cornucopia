// frontend/script.js
const BACKEND_URL = "";

// --- Elements  DOM (Declarats globalment, assignats a initializeDOMElements) ---
let loginForm, usernameInput, passwordInput, loginErrorElement;
let chatForm, preguntaInput, respostaTextElement, respostaContainerElement;
let parrafoModelo, userInfoElement, logoutButton;
let loginSection, chatSection, adminSection;
let ingestForm, convocatoriaUrlInput, convocatoriaNombreInput, ingestStatusElement;
let fileManagementSection, currentIngestingConvocatoriaNameElement, retrievedFilesListElement;
let uploadAdditionalFilesForm, additionalFilesInput, uploadStatusElement;
let confirmProcessButton, cancelIngestButton, processStatusElement;

// Variables globals x estat
let currentIngestingConvocatoriaNombre = null; 
let currentIngestingConvocatoriaUrlOriginal = null;

// --- Funció x inicialitzar var DOM ---
function initializeDOMElements() {
    console.log("LOG_INIT: Iniciando initializeDOMElements...");
    loginForm = document.getElementById("login-form");
    usernameInput = document.getElementById("username");
    passwordInput = document.getElementById("password");
    loginErrorElement = document.getElementById("login-error");
    chatForm = document.getElementById("chat-form");
    preguntaInput = document.getElementById("pregunta");
    respostaTextElement = document.getElementById("resposta");
    respostaContainerElement = document.getElementById("resposta-container");
    parrafoModelo = document.getElementById("modelo-activo");
    userInfoElement = document.getElementById("user-info");
    logoutButton = document.getElementById("logout-button");
    loginSection = document.getElementById("login-section");
    chatSection = document.getElementById("chat-section");
    adminSection = document.getElementById("admin-section");
    ingestForm = document.getElementById("ingest-form");
    convocatoriaUrlInput = document.getElementById("convocatoria-url");
    convocatoriaNombreInput = document.getElementById("convocatoria-nombre");
    ingestStatusElement = document.getElementById("ingest-status");
    fileManagementSection = document.getElementById("file-management-section");
    currentIngestingConvocatoriaNameElement = document.getElementById("current-ingesting-convocatoria-name");
    retrievedFilesListElement = document.getElementById("retrieved-files-list");
    uploadAdditionalFilesForm = document.getElementById("upload-additional-files-form");
    additionalFilesInput = document.getElementById("additional-files-input");
    uploadStatusElement = document.getElementById("upload-status");
    confirmProcessButton = document.getElementById("confirm-process-button");
    cancelIngestButton = document.getElementById("cancel-ingest-button");
    processStatusElement = document.getElementById("process-status");
    console.log("LOG_INIT: Elementos del DOM asignados.");

    // Comprovacions 
    if (!loginForm) console.error("LOG_INIT_ERROR: loginForm NO encontrado!");
    if (!ingestForm && adminSection && adminSection.style.display !== 'none') {
        // Només error si la secció d'admin és visible i el formulari no es troba
        console.error("LOG_INIT_ERROR: ingestForm NO encontrado, pero adminSection podría estar visible!");
    } else if (!ingestForm) {
        console.warn("LOG_INIT_WARN: ingestForm NO encontrado (adminSection podría estar oculta).");
    }
}

// --- Funcions d'UI i autenticació ---
function updateUIForLoginState(isLoggedIn, userRole = "usuario") {
    console.log(`LOG_UI: updateUIForLoginState INVOCADA. isLoggedIn: ${isLoggedIn}, userRole: ${userRole}`);
    const displayLoggedIn = isLoggedIn ? "block" : "none";
    const displayAdminOnly = (isLoggedIn && userRole === "administrador") ? "block" : "none";
    const displayLoggedOut = !isLoggedIn ? "block" : "none";

    if (loginSection) loginSection.style.display = displayLoggedOut; else console.warn("LOG_UI_WARN: loginSection no encontrado.");
    if (chatSection) chatSection.style.display = displayLoggedIn; else console.warn("LOG_UI_WARN: chatSection no encontrado.");
    if (logoutButton) logoutButton.style.display = isLoggedIn ? "inline-block" : "none"; else console.warn("LOG_UI_WARN: logoutButton no encontrado.");
    if (adminSection) adminSection.style.display = displayAdminOnly; else console.warn("LOG_UI_WARN: adminSection no encontrado.");
    
    if (fileManagementSection) { // secció es mostra/amaga per lògica específica
        if (!isLoggedIn || userRole !== "administrador") {
            fileManagementSection.style.display = "none";
        }
    } else { console.warn("LOG_UI_WARN: fileManagementSection no encontrado."); }

    if (!isLoggedIn) {
        if (userInfoElement) userInfoElement.textContent = "";
        if (respostaContainerElement) respostaContainerElement.classList.remove("show");
        if (respostaTextElement) respostaTextElement.textContent = "";
        if (ingestForm) ingestForm.reset();
        if (ingestStatusElement) ingestStatusElement.textContent = "";
    }
    console.log("LOG_UI: updateUIForLoginState FINALIZADA.");
}

async function handleLogin(event) {
    event.preventDefault();
    console.log("LOG_LOGIN: handleLogin invocado.");
    if (!usernameInput || !passwordInput || !loginErrorElement) { console.error("LOG_LOGIN_ERROR: Elementos del form de login no encontrados."); return; }
    const username = usernameInput.value; const password = passwordInput.value;
    loginErrorElement.textContent = "Procesando login..."; loginErrorElement.style.color = "blue";
    try {
        const formData = new URLSearchParams(); formData.append("username", username); formData.append("password", password);
        console.log("LOG_LOGIN: Enviando a /token:", formData.toString());
        const res = await fetch(`${BACKEND_URL}/token`, { method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded", "accept": "application/json"}, body: formData.toString()});
        console.log("LOG_LOGIN: Respuesta de /token. Status:", res.status, "OK:", res.ok);
        if (!res.ok) {
            let errorMsg = `Error de autenticación (${res.status}).`;
            try { const errorData = await res.json(); errorMsg = errorData.detail || errorMsg; } catch (e) {}
            throw new Error(errorMsg);
        }
        const data = await res.json(); console.log("LOG_LOGIN: Datos JSON del token:", data);
        if (data && data.access_token) { 
            localStorage.setItem("access_token", data.access_token); localStorage.setItem("token_type", data.token_type || "bearer");
            console.log("LOG_LOGIN: Token guardado. Llamando a fetchAndDisplayUserInfo...");
            loginErrorElement.textContent = "Login exitoso! Cargando información..."; loginErrorElement.style.color = "green";
            await fetchAndDisplayUserInfo(); 
            console.log("LOG_LOGIN: fetchAndDisplayUserInfo completada después de login.");
        } else { throw new Error("Token de acceso no recibido del servidor."); }
    } catch (error) { console.error("LOG_LOGIN_ERROR: Catch en handleLogin:", error); if (loginErrorElement) { loginErrorElement.textContent = `Error en login: ${error.message}`; loginErrorElement.style.color = "red";}}
}

async function fetchAndDisplayUserInfo() {
    console.log("LOG_FETCH_USER: fetchAndDisplayUserInfo - Iniciando...");
    const token = localStorage.getItem("access_token");
    if (!token) { console.log("LOG_FETCH_USER: No hay token. UI no logada."); updateUIForLoginState(false); return; }
    if (!userInfoElement) { console.error("LOG_FETCH_USER_ERROR: userInfoElement no encontrado!"); updateUIForLoginState(false); return; }
    try {
        console.log("LOG_FETCH_USER: Realizando fetch a /users/me...");
        const res = await fetch(`${BACKEND_URL}/users/me`, { headers: {"Authorization": `Bearer ${token}`} });
        console.log("LOG_FETCH_USER: Respuesta de /users/me. Status:", res.status, "OK:", res.ok);
        if (!res.ok) {
            console.warn("LOG_FETCH_USER: Error en fetch a /users/me. Status:", res.status);
            const errorText = await res.text().catch(()=>"(No se pudo leer cuerpo del error)"); console.warn("LOG_FETCH_USER: Cuerpo error /users/me:", errorText);
            handleLogout(); 
            if(loginErrorElement) loginErrorElement.textContent = (res.status === 401) ? "Sesión expirada. Inicie sesión." : `Error ${res.status} verificando sesión.`;
            return; 
        }
        const userData = await res.json();
        console.log("LOG_FETCH_USER: Datos del usuario:", userData); 
        if (userInfoElement && userData && userData.nom_usuari && userData.rol) { userInfoElement.textContent = `Usuario: ${userData.nom_usuari} (Rol: ${userData.rol})`; }
        else { if (userInfoElement) userInfoElement.textContent = "Usuario: (datos incompletos)";}
        updateUIForLoginState(true, userData.rol);
        console.log("LOG_FETCH_USER: UI actualizada por fetchAndDisplayUserInfo.");
    } catch (error) { console.error("LOG_FETCH_USER_ERROR: Catch en fetchAndDisplayUserInfo:", error); handleLogout(); }
}

function handleLogout() {
    console.log("LOG_LOGOUT: handleLogout invocado.");
    localStorage.removeItem("access_token"); localStorage.removeItem("token_type");
    updateUIForLoginState(false);
    if(respostaTextElement) respostaTextElement.textContent = ""; 
    if(preguntaInput) preguntaInput.value = "";
    if(loginForm) loginForm.reset(); if(ingestForm) ingestForm.reset();
    if(ingestStatusElement) ingestStatusElement.textContent = "";
    if (loginErrorElement) { loginErrorElement.textContent = "Sesión cerrada."; loginErrorElement.style.color = "blue";}
    if(fileManagementSection) fileManagementSection.style.display = "none"; 
}

function displayFileManagementUI(responseData, urlOriginalDeIngesta) {
    console.log("LOG_INGEST_DISPLAY: Mostrando UI de gestión de archivos. Datos:", responseData, "URL Original:", urlOriginalDeIngesta);
    const nombreConvocatoria = responseData.nombre_convocatoria_usado;
    const archivosGestionados = responseData.archivos_gestionados || [];

    if (!fileManagementSection || !currentIngestingConvocatoriaNameElement || !retrievedFilesListElement) {
        console.error("LOG_INGEST_DISPLAY_ERROR: Elementos DOM para gestión de archivos no encontrados.");
        if(ingestStatusElement) ingestStatusElement.textContent = "Error de interfaz: No se pueden mostrar los archivos.";
        return;
    }

    currentIngestingConvocatoriaNombre = nombreConvocatoria; 
    currentConvocatoriaUrlOriginal = urlOriginalDeIngesta; //important!!!!!
    console.log("LOG_INGEST_DISPLAY: currentIngestingConvocatoriaNombre asignado:", currentIngestingConvocatoriaNombre);
    console.log("LOG_INGEST_DISPLAY: currentConvocatoriaUrlOriginal asignada:", currentConvocatoriaUrlOriginal); 

    if(currentIngestingConvocatoriaNameElement) currentIngestingConvocatoriaNameElement.textContent = nombreConvocatoria;
    if(retrievedFilesListElement) retrievedFilesListElement.innerHTML = ""; 

    let archivosEncontradosMostrados = false;
    if (archivosGestionados.length > 0) {
        archivosGestionados.forEach(file => {
            const li = document.createElement("li");
            let fileDescription = file.nombre_original || "Archivo desconocido";
            if (file.tipo === "web_content_file") { 
                fileDescription = `Texto web: ${file.nombre_original}`; 
            } else if (file.tipo === "pdf") { 
                fileDescription = `PDF: ${file.nombre_original}`; 
            } else { 
                fileDescription = `Archivo: ${file.nombre_original} (Tipo: ${file.tipo || 'desconocido'})`; 
            }
            li.textContent = fileDescription;
            if(retrievedFilesListElement) retrievedFilesListElement.appendChild(li);
            archivosEncontradosMostrados = true;
        });
    }
    
    if (!archivosEncontradosMostrados && retrievedFilesListElement) {
         const li = document.createElement("li"); 
         li.textContent = "No se gestionaron archivos automáticamente (ni texto web ni PDFs).";
         retrievedFilesListElement.appendChild(li);
    }

    if (uploadStatusElement) uploadStatusElement.textContent = ""; 
    if (processStatusElement) processStatusElement.textContent = ""; 
    
    if (ingestForm) ingestForm.style.display = "none"; 
    if (fileManagementSection) fileManagementSection.style.display = "block"; 
    
    if (ingestStatusElement) {
        ingestStatusElement.textContent = responseData.message || "Archivos listados. Puede subir adicionales o procesar.";
        ingestStatusElement.style.color = (responseData.errores_encontrados && responseData.errores_encontrados.length > 0) ? "orange" : "green";
    }
    console.log("LOG_INGEST_DISPLAY: UI de gestión de archivos mostrada.");
}

function setupIngestFormListener() {
    console.log("LOG_SETUP: Iniciando setupIngestFormListener.");
    if (ingestForm) { // ingestForm hauria d'haver estat inicialitzat per initializeDOMElements
        console.log("LOG_SETUP: ingestForm ENCONTRADO. Añadiendo event listener...");
        ingestForm.addEventListener("submit", async function(eventIngestForm) {
            console.log("LOG_INGEST_FORM: Event 'submit' de ingestForm CAPTURADO!");
            eventIngestForm.preventDefault(); 
            console.log("LOG_INGEST_FORM: preventDefault() EJECUTADO para ingestForm.");

            if (!convocatoriaUrlInput || !convocatoriaNombreInput || !ingestStatusElement) {
                console.error("LOG_INGEST_FORM_ERROR: Elementos DOM para ingesta (URL, Nombre, Status) no encontrados.");
                return;
            }
            
            const urlOriginal = convocatoriaUrlInput.value; // Guardem URL original
            const nombrePropuesto = convocatoriaNombreInput.value;
            
            if (!urlOriginal.trim() || !nombrePropuesto.trim()) {
                ingestStatusElement.textContent = "La URL y el Nombre de la Convocatoria son obligatorios."; 
                ingestStatusElement.style.color = "red"; 
                return;
            }

            ingestStatusElement.textContent = "Verificando y descargando archivos iniciales...";
            ingestStatusElement.style.color = "orange";
            if (fileManagementSection) fileManagementSection.style.display = "none"; // Amaguem secció d gestió
            
            const token = localStorage.getItem("access_token");
            if (!token) { 
                ingestStatusElement.textContent = "Error: No autenticado. Por favor, inicie sesión."; 
                ingestStatusElement.style.color = "red";
                handleLogout(); 
                return; 
            }

            console.log("LOG_INGEST_FORM: Preparando fetch a /admin/scrape-initial-files...");
            try {
                const res = await fetch(`${BACKEND_URL}/admin/scrape-initial-files`, { 
                    method: "POST", 
                    headers: { 
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ 
                        url_convocatoria: urlOriginal, 
                        nombre_convocatoria_propuesto: nombrePropuesto 
                    })
                });
                
                console.log("LOG_INGEST_FORM: Respuesta de /admin/scrape-initial-files. Status:", res.status, "OK:", res.ok);
                let data;
                try { 
                    data = await res.json(); 
                } catch (e_json) { 
                    console.error("LOG_INGEST_FORM_ERROR: No se pudo parsear JSON de respuesta. Status:", res.status, await res.text().catch(()=>""));
                    if (!res.ok) throw new Error(`Error servidor ${res.status}: ${res.statusText}. Respuesta no es JSON.`);
                    // Si és OK però no JSON, puentejem i  continuem
                    data = { message: "Respuesta del servidor no es JSON, pero la petición fue aceptada. Revise logs.", archivos_gestionados: [], errores_encontrados: ["Respuesta no JSON del servidor"] };
                }
                
                console.log("LOG_INGEST_FORM: Datos recibidos de /admin/scrape-initial-files:", data);

                if (!res.ok) { // errors HTTP com 409 (conflicte) o 500
                    const errorMsg = data.detail || (data && data.message) || `Error del servidor: ${res.status}.`;
                    ingestStatusElement.textContent = `Error: ${errorMsg}`;
                    ingestStatusElement.style.color = "red";
                    
                    if (data && data.conflicto_directorio && data.archivos_en_carpeta_existente) {
                         ingestStatusElement.textContent += ` Archivos en carpeta: ${data.archivos_en_carpeta_existente.join(', ')}`;
                    }
                    return; 
                }
                
                // Èxit scraping/descàrrega (res.ok = true)
                // data és ScrapeResponse del backend
                if (data.archivos_gestionados !== undefined && data.nombre_convocatoria_usado !== undefined) {
                    
                    displayFileManagementUI(data, urlOriginal); // Passem URL original també
                } else {
                    ingestStatusElement.textContent = "Error: La respuesta del servidor no tiene el formato esperado después del scraping.";
                    ingestStatusElement.style.color = "red";
                    console.error("LOG_INGEST_FORM_ERROR: Respuesta inesperada del backend:", data);
                }
            } catch (error) {
                console.error("LOG_INGEST_FORM_ERROR: Catch en listener de ingestForm:", error);
                ingestStatusElement.textContent = `Error en la ingesta inicial: ${error.message}`;
                ingestStatusElement.style.color = "red";
            }
        });
        console.log("LOG_SETUP: Event listener para ingestForm AÑADIDO CORRECTAMENTE.");
    } else { 
        console.error("LOG_SETUP_ERROR: Formulari 'ingest-form' NO encontrado al intentar añadir listener en setupIngestFormListener."); 
    }
}

function setupChatFormListener() {
    console.log("LOG_SETUP: Iniciando setupChatFormListener."); // Log per confirmar execució
    if (chatForm) {
        chatForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            console.log("LOG_CHAT: Event 'submit' de chatForm CAPTURADO!");

            if(!preguntaInput || !respostaTextElement || !respostaContainerElement) {
                console.error("LOG_CHAT_ERROR: Elementos DOM para el chat no encontrados.");
                return;
            }
            const pregunta = preguntaInput.value;
            if (!pregunta.trim()) {
                respostaTextElement.textContent = "Por favor, ingrese una pregunta."; // Espanyol
                respostaTextElement.style.color = "orange";
                respostaContainerElement.classList.add("show");
                return;
            }

            respostaTextElement.textContent = "Procesando su consulta..."; // Espanyol
            respostaTextElement.style.color = "blue"; // Color neutre mentre processa
            respostaContainerElement.classList.remove("show"); // Amaguem per si triga
            respostaContainerElement.classList.add("show"); // Mostrem amb el missatge de processant

            const token = localStorage.getItem("access_token");
            if (!token) {
                respostaTextElement.textContent = "Error: No está autenticado. Por favor, inicie sesión."; // Espanyol
                respostaTextElement.style.color = "red";
                handleLogout(); // Forcem logout
                return;
            }

            try {
                const headers = { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                };
                console.log("LOG_CHAT: Enviando pregunta al backend:", pregunta);
                const res = await fetch(`${BACKEND_URL}/chat`, {
                    method: "POST", 
                    headers: headers, 
                    body: JSON.stringify({ query: pregunta }) 
                });
                
                console.log("LOG_CHAT: Respuesta de /chat. Status:", res.status, "OK:", res.ok);
                let data;
                try {
                    data = await res.json();
                } catch (e_json) {
                    console.error("LOG_CHAT_ERROR: No se pudo parsear JSON de /chat. Status:", res.status);
                    const errorText = await res.text().catch(()=>"Cuerpo de respuesta no legible");
                    console.error("LOG_CHAT_ERROR: Cuerpo de respuesta (no JSON) de /chat:", errorText);
                    throw new Error(`Error del servidor (${res.status}): Respuesta no es JSON válido.`);
                }

                if (!res.ok) {
                    let errorMsg = data.detail || (data && data.message) || `Error del servidor: ${res.status}.`;
                    if (res.status === 401) { 
                        errorMsg = "No autorizado o sesión expirada. Por favor, inicie sesión de nuevo."; // Espanyol
                        handleLogout(); 
                    }
                    throw new Error(errorMsg);
                }
                
                respostaTextElement.textContent = data.respuesta ?? "No se obtuvo respuesta del agente."; // Espanyol
                respostaTextElement.style.color = "#333"; // Restaura color per defecte per a la resposta
                preguntaInput.value = ""; // Neteja l'input després d'enviar

            } catch (error) {
                console.error("LOG_CHAT_ERROR: Catch en listener de chatForm:", error);
                respostaTextElement.textContent = `Error en la consulta: ${error.message}`; // Espanyol
                respostaTextElement.style.color = "red";
            } finally {
                respostaContainerElement.classList.add("show"); // Assegura que el contenidor de resposta sigui visible
            }
        });
        console.log("LOG_SETUP: Listener para chatForm AÑADIDO.");
    } else { 
        console.warn("LOG_SETUP_WARN: Formulario 'chat-form' NO encontrado en setupChatFormListener."); 
    }
}

async function mostrarModeloActivo() { 
    console.log("LOG_MODELO: Iniciando mostrarModeloActivo...");
    if (!parrafoModelo) {
        console.warn("LOG_MODELO_WARN: Elemento 'parrafoModelo' no encontrado. No se mostrará el modelo.");
        return;
    }
    try {
        console.log("LOG_MODELO: Realizando fetch a /model...");
        const res = await fetch(`${BACKEND_URL}/model`); 
        console.log("LOG_MODELO: Respuesta de /model. Status:", res.status, "OK:", res.ok);
        if (!res.ok) {
            let errorMsg = `Error cargando información del modelo (${res.status})`; // Espanyol
            try { 
                const errorData = await res.json(); 
                errorMsg = errorData.detail || errorMsg; 
            } catch (e_json) { /* No fem res si no es pot parsejar */ }
            throw new Error(errorMsg);
        }
        const data = await res.json();
        console.log("LOG_MODELO: Datos del modelo recibidos:", data);
        parrafoModelo.textContent = `Modelo activo: ${data.llm_provider || 'No especificado'} (${data.model || 'No especificado'})`; // Més robust
    } catch (error) { 
        console.error("LOG_MODELO_ERROR: Error obteniendo el modelo activo:", error); 
        parrafoModelo.textContent = `Error al cargar información del modelo: ${error.message}`; // Espanyol
    }
}

function setupFileManagementListeners() {
    console.log("LOG_SETUP: Iniciando setupFileManagementListeners.");

    if (uploadAdditionalFilesForm) { 
        uploadAdditionalFilesForm.addEventListener("submit", async function(event) { 
            console.log("LOG_UPLOAD_FORM: Event 'submit' de uploadAdditionalFilesForm CAPTURADO!"); // NOU LOG
            event.preventDefault(); 
            console.log("LOG_UPLOAD_FORM: preventDefault() EJECUTADO para uploadAdditionalFilesForm."); // NOU LOG

            if (!additionalFilesInput || !uploadStatusElement || !currentIngestingConvocatoriaNombre) {
                if(uploadStatusElement) {
                    uploadStatusElement.textContent = "Error: No hay convocatoria activa o falta el campo de subida.";
                    uploadStatusElement.style.color = "red";
                }
                return;
            }
            const files = additionalFilesInput.files;
            if (files.length === 0) {
                if(uploadStatusElement) {
                    uploadStatusElement.textContent = "Por favor, seleccione al menos un archivo.";
                    uploadStatusElement.style.color = "orange";
                }
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }

            if(uploadStatusElement) {
                uploadStatusElement.textContent = "Subiendo archivos...";
                uploadStatusElement.style.color = "orange";
            }
            const token = localStorage.getItem("access_token");
            if (!token) { 
                if(uploadStatusElement) uploadStatusElement.textContent = "Error: No autenticado.";
                handleLogout(); 
                return; 
            }

            // Utilitzem  crida directa al backend (port 8000), nginx ens bloquejava.  Mala pràxis
            const UPLOAD_ENDPOINT_URL = `http://localhost:8000/admin/upload-additional-file/${currentIngestingConvocatoriaNombre}`;
            console.log("LOG_UPLOAD: Subiendo archivos directamente a:", UPLOAD_ENDPOINT_URL);

            try {
                const res = await fetch(UPLOAD_ENDPOINT_URL, {
                    method: "POST",
                    headers: { "Authorization": `Bearer ${token}` }, // No Content-Type aquí per a FormData
                    body: formData
                });

                const data = await res.json(); 
                console.log("LOG_UPLOAD: Respuesta del backend (directa) para subida:", data);

                if (!res.ok) {
                    throw new Error(data.detail || data.message || `Error subiendo archivos: ${res.status}`);
                }

                if(uploadStatusElement) {
                    uploadStatusElement.textContent = data.message || "Archivos subidos correctamente.";
                    uploadStatusElement.style.color = (data.errors && data.errors.length > 0) ? "orange" : "green";
                }
                
                if (data.uploaded_filenames && retrievedFilesListElement) {
                    data.uploaded_filenames.forEach(filename => {
                        const li = document.createElement("li");
                        li.textContent = `SUBIDO MANUALMENTE: ${filename}`;
                        li.style.fontStyle = "italic";
                        li.style.color = "darkblue"; 
                        retrievedFilesListElement.appendChild(li);
                    });
                }
                uploadAdditionalFilesForm.reset();

            } catch (error) {
                console.error("Error subiendo archivos directamente al backend:", error);
                if(uploadStatusElement) {
                    uploadStatusElement.textContent = `Error al subir (directo): ${error.message}`;
                    uploadStatusElement.style.color = "red";
                }
            }
        });
        console.log("LOG_SETUP: Listener para uploadAdditionalFilesForm OK (modo envío múltiple directo).");
    } else { 
        console.warn("LOG_SETUP_WARN: uploadAdditionalFilesForm NO encontrado."); 
    }

    if (confirmProcessButton) { 
        confirmProcessButton.addEventListener("click", async function() { 
            console.log("LOG_CONFIRM_PROCESS: Botón 'Confirmar y Procesar' CLICADO!");
            console.log("LOG_CONFIRM_PROCESS: Usando nombre:", currentIngestingConvocatoriaNombre);
            console.log("LOG_CONFIRM_PROCESS: Usando URL original:", currentConvocatoriaUrlOriginal);

            if (!currentIngestingConvocatoriaNombre || !currentConvocatoriaUrlOriginal) {
                if(processStatusElement) {
                    processStatusElement.textContent = "Error: Falta información de la convocatoria (nombre o URL original). Intente la ingesta inicial de nuevo."; // Espanyol
                    processStatusElement.style.color = "red";
                }
                console.error("LOG_CONFIRM_PROCESS_ERROR: Falta nombre_convocatoria o url_original.");
                return;
            }

            if(processStatusElement) {
                processStatusElement.textContent = "Iniciando procesamiento final e inserción en la BD (esto puede tardar)..."; 
                processStatusElement.style.color = "orange";
            }
            const token = localStorage.getItem("access_token");
            if (!token) { 
                if(processStatusElement) processStatusElement.textContent = "Error: No autenticado."; 
                handleLogout(); 
                return; 
            }

            console.log("LOG_CONFIRM_PROCESS: Preparando fetch a /admin/process-documents-for-db");
            try {
                const res = await fetch(`${BACKEND_URL}/admin/process-documents-for-db`, { 
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}`},
                    body: JSON.stringify({ 
                        nombre_convocatoria: currentIngestingConvocatoriaNombre,
                        convocatoria_url_original: currentConvocatoriaUrlOriginal
                    })
                });
                
                console.log("LOG_CONFIRM_PROCESS: Respuesta de /admin/process-documents-for-db. Status:", res.status, "OK:", res.ok);
                let data;
                try {
                    data = await res.json();
                    console.log("LOG_CONFIRM_PROCESS: Datos de /admin/process-documents-for-db:", data);
                } catch (e_json) {
                    console.error("LOG_CONFIRM_PROCESS_ERROR: No se pudo parsear JSON de respuesta. Status:", res.status);
                    const errorText = await res.text().catch(()=>"Cuerpo de respuesta no legible");
                    console.error("LOG_CONFIRM_PROCESS_ERROR: Cuerpo de respuesta (no JSON):", errorText);
                    throw new Error(`Error del servidor (${res.status}): Respuesta no es JSON válido.`);
                }

                if (!res.ok) {
                    throw new Error(data.detail || data.message || `Error del servidor procesando documentos: ${res.status}`);
                }

                if(processStatusElement) {
                    processStatusElement.textContent = data.message || "Procesamiento finalizado."; 
                    if (data.status_code_internal && data.status_code_internal >= 207 || (data.errores_procesamiento_bd && data.errores_procesamiento_bd.length > 0) ) {
                        processStatusElement.style.color = "orange"; 
                    } else {
                        processStatusElement.style.color = "green"; 
                    }
                }
                
                if(fileManagementSection) fileManagementSection.style.display = "none";
                if(ingestForm) { ingestForm.reset(); ingestForm.style.display = "block"; }
                if(ingestStatusElement) ingestStatusElement.textContent = "Proceso completado. Puede ingresar una nueva convocatoria."; // Espanyol
                currentIngestingConvocatoriaNombre = null; 
                currentConvocatoriaUrlOriginal = null;

            } catch (error) {
                console.error("LOG_CONFIRM_PROCESS_ERROR: Catch en listener de confirmProcessButton:", error);
                if(processStatusElement) {
                    processStatusElement.textContent = `Error en el procesamiento final: ${error.message}`; 
                    processStatusElement.style.color = "red";
                }
            }
        });
        console.log("LOG_SETUP: Listener para confirmProcessButton OK.");
    } else { 
        console.error("LOG_SETUP_ERROR: confirmProcessButton NO encontrado!"); 
    }

    if (cancelIngestButton) { // O resetIngestButton si canvieml'ID
        cancelIngestButton.addEventListener("click", function() { 
            console.log("LOG_RESET_INGEST: Botón 'Reiniciar Ingesta' CLICADO!");

            // No cal confirmació si només reseteja la UI
            // if (!confirm(`¿Seguro que desea reiniciar el proceso de ingesta? Los archivos en el servidor no se borrarán.`)) return;

            if(processStatusElement) {
                processStatusElement.textContent = "Proceso de ingesta reiniciado.";
                processStatusElement.style.color = "blue";
            }

            // Amaguem  secció gestió i mostrem la d'ingesta inicial
            if(fileManagementSection) fileManagementSection.style.display = "none";
            if(ingestForm) { 
                ingestForm.reset(); // Neteja el formulari d'URL i Nom
                ingestForm.style.display = "block"; 
            }
            if(ingestStatusElement) ingestStatusElement.textContent = "Introduzca una nueva URL y nombre para la convocatoria."; // Missatge inicial

            // Resetejem variables globals de ingesta actual
            currentIngestingConvocatoriaNombre = null; 
            currentConvocatoriaUrlOriginal = null;
            if(retrievedFilesListElement) retrievedFilesListElement.innerHTML = ""; // Neteja llista de fitxers
            if(uploadAdditionalFilesForm) uploadAdditionalFilesForm.reset(); // Neteja input de pujada de fitxers
            if(uploadStatusElement) uploadStatusElement.textContent = "";

            console.log("LOG_RESET_INGEST: UI de ingesta reiniciada.");
        });
        console.log("LOG_SETUP: Listener para resetIngestButton (antes cancel) OK.");
    } else { 
        console.error("LOG_SETUP_ERROR: resetIngestButton (antes cancel) NO encontrado!"); 
    }
}

function setupEventListeners() {
    console.log("LOG_SETUP: Iniciando setupEventListeners...");
    if (loginForm) { loginForm.addEventListener("submit", handleLogin); console.log("LOG_SETUP: Listener loginForm OK.");} 
    else { console.error("LOG_SETUP_ERROR: loginForm NO encontrado!"); }
    if (logoutButton) { logoutButton.addEventListener("click", handleLogout); console.log("LOG_SETUP: Listener logoutButton OK.");}
    else { console.warn("LOG_SETUP_WARN: logoutButton NO encontrado.");}
    setupIngestFormListener(); 
    setupChatFormListener();   
    setupFileManagementListeners();
    console.log("LOG_SETUP: Todos los listeners principales configurados.");
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("LOG_INIT: DOMContentLoaded event disparat.");
    initializeDOMElements(); 
    setupEventListeners(); 
    fetchAndDisplayUserInfo(); 
    mostrarModeloActivo();
    console.log("LOG_INIT: Script cargado y todos los listeners configurados.");
});