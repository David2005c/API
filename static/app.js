
const API_URL = "";

const catalogGrid = document.getElementById("catalog-grid");
const catalogMessage = document.getElementById("catalog-message");
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchResult = document.getElementById("search-result");
const reloadButton = document.getElementById("reload-button");
const sortSelect = document.getElementById("sort-select");
const detailsDialog = document.getElementById("details-dialog");
const detailsContent = document.getElementById("details-content");
const closeDialog = document.getElementById("close-dialog");

let catalogo = [];
let filtroActual = "Todos";

// Evita insertar contenido del catálogo como HTML ejecutable.
function escaparHTML(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, caracter => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[caracter]);
}

// Petición GET para obtener todos los títulos.
async function cargarCatalogo() {
    catalogMessage.textContent = "Cargando catálogo...";
    catalogMessage.className = "message";
    catalogGrid.innerHTML = "";
    reloadButton.disabled = true;

    try {
        const respuesta = await fetch(`${API_URL}/peliseries`);

        if (!respuesta.ok) {
            throw new Error(`Error HTTP ${respuesta.status}`);
        }

        catalogo = await respuesta.json();

        if (!Array.isArray(catalogo)) {
            throw new Error("La API no ha devuelto una lista de títulos.");
        }

        mostrarCatalogo();
    } catch (error) {
        catalogMessage.textContent =
            "No se ha podido cargar el catálogo. Comprueba que FastAPI esté funcionando.";
        catalogMessage.className = "message error";

        console.error("Error al cargar el catálogo:", error);
    } finally {
        reloadButton.disabled = false;
    }
}

// Aplica filtros y ordenación antes de dibujar las tarjetas.
function obtenerTitulosVisibles() {
    let titulos = [...catalogo];

    if (filtroActual !== "Todos") {
        titulos = titulos.filter(
            pelicula => pelicula.tipo === filtroActual
        );
    }

    switch (sortSelect.value) {
        case "score":
            titulos.sort((a, b) => b.score - a.score);
            break;

        case "year":
            titulos.sort((a, b) => b.anio - a.anio);
            break;

        case "title":
            titulos.sort((a, b) =>
                a.titulo.localeCompare(b.titulo, "es")
            );
            break;
    }

    return titulos;
}

// Dibuja las tarjetas del catálogo.
function mostrarCatalogo() {
    const titulos = obtenerTitulosVisibles();

    catalogGrid.innerHTML = "";

    if (titulos.length === 0) {
        catalogMessage.textContent = catalogo.length
            ? "No hay títulos que coincidan con este filtro."
            : "El catálogo está vacío.";

        catalogMessage.className = "message";
        return;
    }

    catalogMessage.textContent =
        `${titulos.length} título${titulos.length === 1 ? "" : "s"} encontrado${titulos.length === 1 ? "" : "s"}.`;
    catalogMessage.className = "message";

    catalogGrid.innerHTML = titulos.map((pelicula) => `
        <article class="movie-card">
            <div class="card-top">
                <span class="type-badge">
                    ${escaparHTML(pelicula.tipo)}
                </span>

                <span class="score">
                    ★ ${Number(pelicula.score).toFixed(1)}
                </span>
            </div>

            <h3>${escaparHTML(pelicula.titulo)}</h3>

            <p class="movie-year">
                ${escaparHTML(pelicula.anio)}
            </p>

            <p class="genre">
                ${escaparHTML(pelicula.genero)}
            </p>

            <div class="card-footer">
                <span class="seen-status ${pelicula.vista ? "seen" : ""}">
                    ${pelicula.vista ? "✓ Vista" : "○ Pendiente"}
                </span>

                <button
                    class="details-button"
                    type="button"
                    data-title="${escaparHTML(pelicula.titulo)}"
                >
                    Ver detalles →
                </button>
            </div>
        </article>
    `).join("");
}

// POST: busca un título enviando solo el título en JSON.
async function buscarTitulo(titulo) {
    searchResult.innerHTML = `
        <p class="message">Buscando "${escaparHTML(titulo)}"...</p>
    `;

    try {
        const respuesta = await fetch(`${API_URL}/buscar_peliserie`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ titulo })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.detail || datos.mensaje || "No se ha encontrado el título."
            );
        }

        searchResult.innerHTML = `
            <article class="search-result-card">
                <div>
                    <span class="eyebrow">RESULTADO DE BÚSQUEDA</span>
                    <h3>${escaparHTML(datos.titulo)}</h3>
                    <p>
                        ${escaparHTML(datos.tipo)} ·
                        ${escaparHTML(datos.anio)} ·
                        ${escaparHTML(datos.genero)}
                    </p>
                    <p class="score" style="margin-top: 10px;">
                        ★ ${Number(datos.score).toFixed(1)} / 10
                    </p>
                    <p>
                        ${datos.vista ? "✓ Ya la has visto" : "○ Pendiente de ver"}
                    </p>
                </div>

                <button
                    class="button button-secondary"
                    type="button"
                    id="search-details-button"
                >
                    Ver ficha completa
                </button>
            </article>
        `;

        document.getElementById("search-details-button")
            .addEventListener("click", () => mostrarDetalles(datos));

    } catch (error) {
        searchResult.innerHTML = `
            <p class="message error">
                ${escaparHTML(error.message)}
            </p>
        `;

        console.error("Error en la búsqueda:", error);
    }
}

// GET: consulta los datos de un título concreto.
// async function consultarInfo(titulo) {
    
//     try {
//         const respuesta = await fetch(
//             `${API_URL}/info?titulo=${encodeURIComponent(titulo)}`
//         );

//         const datos = await respuesta.json();

//         if (!respuesta.ok) {
//             throw new Error(
//                 datos.detail || "No se ha encontrado el título."
//             );
//         }

//         mostrarDetalles(datos);
//     } catch (error) {
//         alert(error.message);
//         console.error("Error al consultar la información:", error);
//     }
// }

// Muestra todos los datos en una ventana emergente.
function mostrarDetalles(pelicula) {
    detailsContent.innerHTML = `
        <span class="eyebrow">FICHA DEL TÍTULO</span>
        <h2>${escaparHTML(pelicula.titulo)}</h2>

        <span class="type-badge">
            ${escaparHTML(pelicula.tipo)}
        </span>

        <ul class="details-list">
            <li>
                <span>Año</span>
                <strong>${escaparHTML(pelicula.anio)}</strong>
            </li>
            <li>
                <span>Género</span>
                <strong>${escaparHTML(pelicula.genero)}</strong>
            </li>
            <li>
                <span>Puntuación</span>
                <strong>★ ${Number(pelicula.score).toFixed(1)} / 10</strong>
            </li>
            <li>
                <span>Estado</span>
                <strong>${pelicula.vista ? "Vista" : "Pendiente"}</strong>
            </li>
        </ul>
    `;

    detailsDialog.showModal();
}

// Eventos de búsqueda.
searchForm.addEventListener("submit", event => {
    event.preventDefault();

    const titulo = searchInput.value.trim();

    if (titulo.length < 2 || titulo.length > 50) {
        searchInput.reportValidity();
        return;
    }

    buscarTitulo(titulo);
});

// Filtros por tipo.
document.querySelectorAll(".filter-button").forEach(boton => {
    boton.addEventListener("click", () => {
        filtroActual = boton.dataset.filter;

        document.querySelectorAll(".filter-button").forEach(item => {
            item.classList.toggle("active", item === boton);
        });

        mostrarCatalogo();
    });
});

// Ordenación.
sortSelect.addEventListener("change", mostrarCatalogo);

// Actualizar catálogo.
reloadButton.addEventListener("click", cargarCatalogo);

// Abrir detalles desde una tarjeta.
catalogGrid.addEventListener("click", event => {
    const boton = event.target.closest(".details-button");

    if (boton) {
        const titulo = boton.dataset.title;

        const pelicula = catalogo.find(
            p => p.titulo === titulo
        );

        if (pelicula) {
            mostrarDetalles(pelicula);
        }
    }
});

// Cerrar ventana de detalles.
closeDialog.addEventListener("click", () => {
    detailsDialog.close();
});

detailsDialog.addEventListener("click", event => {
    if (event.target === detailsDialog) {
        detailsDialog.close();
    }
});

// Cargar el catálogo al abrir la página.
cargarCatalogo();

async function consultarProbabilidad(titulo) {
    const genero = document.getElementById("favorite-genre").value;
    const tipo = document.getElementById("preferred-type").value;
    const resultado = document.getElementById("probability-result");
    const boton = document.getElementById("calculate-score");

    resultado.textContent = "Calculando...";
    boton.disabled = true;

    try {
        const respuesta = await fetch(
            `${API_URL}/probabilidad_gusto`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    titulo: titulo,
                    genero_favorito: genero || null,
                    tipo_preferido: tipo || null
                })
            }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.detail || "No se pudo calcular el score."
            );
        }

        resultado.innerHTML = `
            <p class="probability-value">
                ${datos.probabilidad_estimada} %
            </p>
            <p>Probabilidad estimada de que te guste</p>
            <ul>
                ${datos.explicacion.map(
                    texto => `<li>${escaparHTML(texto)}</li>`
                ).join("")}
            </ul>
        `;

    } catch (error) {
        resultado.textContent = error.message;
        console.error(error);
    } finally {
        boton.disabled = false;
    }
}