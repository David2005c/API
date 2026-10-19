from fastapi import FastAPI

# 1. Instanciamos la aplicación FastAPI
app = FastAPI(
    title="API de Introducción a la IA",
    description="Servicio web para consultar el estado del sistema y realizar pruebas de endpoints",
    version="1.0.0"
)

# 2. Definimos nuestro primer endpoint (Ruta raíz)
@app.get("/home")
def ruta_raiz():
    """
    Endpoint principal de bienvenida.
    Devuelve un mensaje en formato JSON.
    """
    return {
        "mensaje": "¡Bienvenido a la API de Inteligencia Artificial soy David!",
        "version": "1.0.0",
        "estado": "operativo"
    }

# 3. Endpoint de comprobación de salud del servicio (Health Check)
@app.get("/health")
def estado_servicio():
    return {
        "estado": "OK",
        "memoria_disponible": "85%",
        "modelos_cargados": 0
    }

@app.get("/modelos/{modelo_id}")
def obtener_informacion_modelo(modelo_id: int):
    """
    Devuelve la información de un modelo según su identificador numérico.
    """
    catalogo = {
        1: {"nombre": "Clasificador_Clientes", "algoritmo": "RandomForest", "precision": 0.92},
        2: {"nombre": "Detector_Anomalias", "algoritmo": "IsolationForest", "precision": 0.88}
    }
    
    if modelo_id in catalogo:
        return {"encontrado": True, "modelo": catalogo[modelo_id]}
    
    return {"encontrado": False, "mensaje": "Modelo no disponible en el catálogo"}

@app.get("/predicciones/")
def consultar_historial(limite: int = 10, categoria: str = "general"):
    """
    Simula la consulta de predicciones con paginación y filtro opcional.
    """
    return {
        "limite_solicitado": limite,
        "categoria_filtro": categoria,
        "total_registros": 45
    }