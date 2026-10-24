from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Literal
from pydantic import BaseModel, Field

# ==========================================
# 1. Esquemas de datos con Pydantic
# ==========================================

# Esquema de entrada (Validación estricta)
class Buscador( BaseModel):
    titulo: str = Field(min_length=2, max_length=50, description="titulo de la película/serie")
    # anio: int = Field(ge=1980, le=2026, description="Año de la película/serie")
    # score: float = Field(gt=0, description="Valoración de la película/serie")
    # genero: str = Field(min_length=5, max_length=50, description="Género de la película/serie")
    # tipo: str = Field(description='Película o serie')
    # vista: bool = Field(default=False, description='¿Has visto la película/serie?')
    

# Esquema de respuesta tipado
class ResultadoBusqueda(BaseModel):
    titulo: str = Field(min_length=2, max_length=50, description="titulo de la película/serie")
    anio: int = Field(ge=1980, le=2026, description="Año de la película/serie")
    score: float = Field(gt=0, description="Valoración de la película/serie")
    genero: str = Field(min_length=5, max_length=50, description="Género de la película/serie")
    tipo: str = Field(description='Película o serie')
    vista: bool = Field(default=False, description='¿Has visto la película/serie?')

class Probabilidad(BaseModel):
    titulo: str = Field(min_length=2, max_length=50)
    genero_fav: str | None = None
    tipo_pref : Literal['Película','Serie'] | None = None

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
    ResultadoBusqueda( 
        titulo='Star Wars',
        anio=2006,
        genero='Acción',
        score=9.2,
        tipo='Película',
        vista=False
    ),
    ResultadoBusqueda( 
        titulo='Crimen en el paraíso',
        anio=2011,
        genero='Misterio/Drama',
        score=9.6,
        tipo='Serie',
        vista=False
    ),
    ResultadoBusqueda( 
        titulo='Avatar 3: Fuego y Cenizas',
        anio=2025,
        genero='Acción/Aventuras',
        score=8.4,
        tipo='Película',
        vista=False
    ),
    ResultadoBusqueda(        
        titulo='Lioness',
        anio=2023,
        genero='Acción/Drama/Suspenso/Thriller',
        score=8.4,
        tipo='Serie',
        vista=False
    ),
    ResultadoBusqueda( 
        titulo='Space Jam',
        anio=1996,
        genero='Animación/Comedia/Deportes',
        score=7.7,
        tipo='Película',
        vista=False
    ),
    ResultadoBusqueda(
        titulo='Stranger Things',
        anio=2016,
        genero='Terror/Drama/Suspense',
        score=8.6,
        tipo='Serie',
        vista=False
    )
]

# Ruta raíz: sirve la interfaz visual del simulador
@app.get("/", response_class=FileResponse)
def inicio():
    return FileResponse("index.html")

if __name__ == "__main__":
    # El host 0.0.0.0 es la clave para que sea accesible en tu red local
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

# 1. Endpoint que devuelve todo el catálogo
@app.get("/peliseries", response_model=list[ResultadoBusqueda])
def obtener_peliseries():
    
    return catalogo

# 2. Endpoint para una bucar una película/serie en el catálogo
@app.post("/buscar_peliserie", response_model=ResultadoBusqueda)
def buscar_peliserie(busqueda: Buscador):
    """
    Busca una película o serie que quieras ver.
    """
    for pelicula in catalogo:
        if pelicula.titulo.lower() == busqueda.titulo.lower():
            return {
                "titulo": pelicula.titulo,
                "anio": pelicula.anio,
                "genero": pelicula.genero,
                "tipo": pelicula.tipo,
                "score": pelicula.score
            }

# 3. Endpoint para calcular la probabilidad de que al usuario le gusta una película/serie

@app.post("/probabilidad", response_model=Probabilidad)
def probabilidad_gustar(busqueda: Probabilidad):

    pelicula=next(
        (
            peli for peli in catalogo
            if peli.titulo.lower==busqueda.titulo.lower

        )
    ), None

    puntos=(pelicula*10)/50

    explicacion=[]

    explicacion.append(
        f"Puntuación:{pelicula.score}/10"
    )

    if busqueda.genero_fav:
        coincide_genero=(
            busqueda.genero_fav.lower() in pelicula.genero.lower
        )

    if coincide_genero:

        puntos +=35

        explicacion.append("Es tu género favorito")
    else:
        explicacion.append("No es tu género favorito")  

    if busqueda.tipo_pref:
        
        puntos +=15

        explicacion.append("Es tu tipo preferido")
    else:
        explicacion.append("No es tu tipo preferido") 

    maximo=50

    if busqueda.genero_fav:
        maximo+=35

    if busqueda.tipo_pref:
        maximo+=15

    porcentaje=round((puntos/maximo)*100,1)

    return{
        'titulo':busqueda.titulo,
        'probabilidad':porcentaje,
        'explicacion':explicacion
    }

# 4. Endpoint de comprobación de salud del servicio (Health Check)
@app.get("/check")
def estado_servicio():
    return {
        "estado": "OK",
        "memoria_disponible": "85%",
        "modelos_cargados": 1
    }

# http://192.168.1.16:8000