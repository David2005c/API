from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ==========================================
# 1. Esquemas de datos con Pydantic
# ==========================================

# Esquema de entrada (Validación estricta)
class Buscador(BaseModel):
    titulo: str = Field(min_length=2, max_length=50, description="titulo de la película/serie")
    anio: int = Field(ge=1980, le=2026, description="Año de la película/serie")
    score: float = Field(gt=0, description="Valoración de la película/serie")
    genero: str = Field(min_length=5, max_length=20, description="Género de la película/serie")
    tipo: str = Field(description='Película o serie')
    vista: bool = Field(default=False,description='¿Has visto la película/serie?')
    

# Esquema de respuesta tipado
class ResultadoBusqueda(BaseModel):
    titulo: str
    anio: int
    score: float
    genero: str
    tipo: str
    vista: bool

# ==========================================
# 2. Servidor FastAPI, CORS y Estáticos
# ==========================================

app = FastAPI(
    title="CineAPI",
    description="API para buscar una serie o película que el usuario quiere ver",
    version="1.0.0"
)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Montamos la carpeta static para servir el código JavaScript y estilos
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 3. Endpoints del servicio y Frontend
# ==========================================

catalogo=[
    {
        "titulo": 'Star Wars',
        "año": 2006,
        "genero": 'Acción',
        "score": 9.2,
        "tipo": 'Película',
        "vista": False
    },
    {
        "titulo": 'Crimen en el paraíso',
        "año": 2011,
        "genero": 'Misterio/Drama',
        "score": 9.6,
        "tipo": 'Serie',
        "vista": False
    },
    {
        "titulo": 'Avatar 3: Fuego y Cenizas',
        "año": 2025,
        "genero": 'Acción/Aventuras',
        "score": 8.4,
        "tipo": 'Película',
        "vista": False
    },
    {
        "titulo": 'Lioness',
        "año": 2023,
        "genero": 'Acción/Drama/Suspenso/Thriller',
        "score": 8.4,
        "tipo": 'Serie',
        "vista": False
    },
    {
        "titulo": 'Space Jam',
        "año": 1996,
        "genero": 'Animación/Comedia/Deportes',
        "score": 7.7,
        "tipo": 'Película',
        "vista": False
    },
]

# Ruta raíz: sirve la interfaz visual del simulador
@app.get("/", response_class=FileResponse)
def inicio():
    return FileResponse("index.html")


@app.get("/peliseries")
def obtener_peliseries():
    
    return catalogo

@app.get("/info")
def obtener_info(titulo:str):
    for pelicula in catalogo:
        if pelicula["titulo"].lower() == titulo.lower():
            return {
                "titulo": pelicula["titulo"],
                "año": pelicula["año"],
                "genero": pelicula["genero"],
                "tipo": pelicula["tipo"],
                "score": pelicula["score"]
            }

@app.post("/buscar_peliserie", response_model=ResultadoBusqueda)
def buscar_peliserie(busqueda: Buscador):
    """
    Busca una película o serie que quieras ver.
    """


    return {
        "titulo": busqueda.titulo,
        "genero": busqueda.genero,
        "año": busqueda.anio,
        "tipo": busqueda.tipo,
        "vista": busqueda.vista,
        "score": busqueda.score
    }

