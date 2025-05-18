import datetime
from typing import Dict, Any, TypedDict
import os
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
import requests
import google.generativeai as genai
import json
import re  # Importa el módulo re para expresiones regulares
from flask import Flask, request, jsonify

SQL_API = os.getenv("SQL_API", "https://sql-api-1034485564291.europe-west1.run.app")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "default-key")

# --- Define State Schema ---
class State(TypedDict):
    message: HumanMessage
    betting_amount: float
    current_date: datetime.date
    api_response: str
    betting_recommendation: str
    output: str

# --- 1. Fetch Data from API Tool & Node ---
class FetchDataFromAPITool(BaseTool):
    name: str = "fetch_data_from_api"
    description: str = "Obtiene los datos de la API externa."

    def _run(self, tool_input: dict = {}) -> str:
        # print("\n[Llamada a la Herramienta] Obteniendo datos de la API...")
        api_url = SQL_API
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.text
            return data
        except requests.exceptions.RequestException as e:
            error_message = f"Error al obtener datos de la API: {e}"
            print(error_message)
            return error_message

    async def _arun(self) -> str:
        raise NotImplementedError("Asíncrono no soportado para esta herramienta")

fetch_data_tool = FetchDataFromAPITool()

def fetch_data_from_api_node(state: State) -> Dict[str, str]:
    """Llama a la API externa para obtener todos los datos necesarios."""
    # print("\n--- Nodo: Obtener Datos de la API ---")
    result = fetch_data_tool.run({})
    return {"api_response": result}

# --- 2. Reasoning Node ---
def reasoning_node(state: State) -> Dict[str, str]:
    """Genera recomendaciones de apuestas utilizando un LLM (Gemini)."""
    # print("\n--- Nodo: Razonamiento ---")
    # print("Generando estrategia de apuestas con Gemini...")

    api_response_str = state.get("api_response", "{}")
    budget = state.get("betting_amount", 0.0)

    try:
        api_data = json.loads(api_response_str) if api_response_str else {}
    except json.JSONDecodeError as e:
        error_message = f"Error al analizar la respuesta de la API como JSON: {e}"
        print(error_message)
        return {"betting_recommendation": "Error: La API no devolvió un formato JSON válido."}

    if not isinstance(api_data, dict):
        return {"betting_recommendation": "Error: La API no devolvió un diccionario."}

    try:
        api_key = GEMINI_API_KEY
        if not api_key:
            return {"betting_recommendation": {"error": "No se encontró la variable de entorno GEMINI_API_KEY"}}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
Eres un experto en apuestas deportivas de la NBA, altamente capacitado para analizar diversos datos y generar estrategias de apuestas óptimas. Tu objetivo es maximizar las ganancias del usuario minimizando el riesgo.
La cantidad total de dinero que el usuario desea apostar es {budget} euros.
Se te proporcionará la siguiente información: {api_data}, la cual contiene un json con los siguientes campos:
"game_odds": En esta parte del diccionario nos interesa:
    * bookmaker_name: Nombre de la casa de apuestas.
    * Dentro de outcomes, nos interesa el campo name, el cual contiene el nombre de ambos equipos y price, el cual contiene la cuota de cada equipo.
"injured_players": En esta parte del diccionario nos interesa:
    * Saber que id de team corresponde a cada equipo (el id de cada equipo corresponde al segundo numero de injuered players, ej :1610612738 ), para poder hacer la relación con los partidos, además aparece la abreviacion de cada equipo. Y el nombre de cada jugador lesionado. Al estado de la lesion no lo tendremos en cuenta, todos los jugadores que aparezcan en "injured_players" se consideraran lesionados.
"nba_games_week": En esta parte del diccionario nos interesa:
    * Los equipos que se enfrentan, por lo que aparece la abreviacion de cada equipo y el id de cada equipo. El equipo que aparece primero es el local y el segundo el visitante.
"predictions": En esta parte del diccionario nos interesa:
    * El id de cada equipo, lo cual corresponde al primer valor que aparece, y la prediccion de puntos que se espera que haga cada equipo, el cual corresponde al tercer valor que aparece.

Tu tarea es generar una estrategia de apuestas para la semana, determinando para cada partido de "nba_games_week".

Devuelve SOLO un objeto JSON válido sin ningún texto adicional ni bloques de código markdown. El objeto debe tener las llaves exteriores, sin ningún formato adicional como ```json o ```.

El objeto JSON debe tener la siguiente estructura:
Para el partido y para el equipo ganador,  quiero que utilices el nombre completo de cada equipo, y no la abreviación. Para la odd necesito que me saques el valor para el cual tiene esa apuesta esa casa de apuesta
{{
    "estrategia": [
        {{
            "partido": "Equipo A vs Equipo B",
            "ganador": "Equipo A",
            "casa_de_apuestas": "Casa1",
            "odds": 1.5,
            "cantidad_a_apostar": 25.00
        }},
        {{
            "partido": "Equipo C vs Equipo D",
            "ganador": "Equipo D",
            "casa_de_apuestas": "Casa2",
            "odds": 2.0,
            "cantidad_a_apostar": 30.00
        }}
    ]
}}
"""

        response = model.generate_content(prompt)
        llm_response = response.text

        # Extraer JSON de bloques de código si existen
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, llm_response)
        
        if json_match:
            # Si encontramos un bloque de código JSON, extraemos su contenido
            llm_response = json_match.group(1).strip()
        else:
            # Si no hay bloques de código, limpiamos la respuesta
            llm_response = llm_response.strip()
        
        # Verificar si la respuesta comienza directamente con el JSON
        if not llm_response.startswith('{'):
            # Buscar el primer carácter '{' para eliminar cualquier texto preliminar
            start_idx = llm_response.find('{')
            if start_idx != -1:
                llm_response = llm_response[start_idx:]
        
        try:
            # Intentar cargar el JSON
            llm_response_dict = json.loads(llm_response)
            
            # Verificar que tenga la estructura esperada
            if not isinstance(llm_response_dict, dict):
                raise ValueError("La respuesta del LLM no es un diccionario.")
                
            recommendations = llm_response_dict.get("estrategia", [])
            if not isinstance(recommendations, list):
                raise ValueError("La respuesta del LLM no contiene una lista de recomendaciones.")
                
            # Guardar directamente las recomendaciones en el estado
            return {"betting_recommendation": llm_response_dict}
            
        except (ValueError, json.JSONDecodeError) as e:
            # Devolvemos un mensaje de error sin imprimir nada aquí
            return {"betting_recommendation": {"error": f"Error al analizar la respuesta del LLM: {e}"}}

    except Exception as e:
        # Devolvemos un mensaje de error sin imprimir nada aquí
        return {"betting_recommendation": {"error": f"Error al generar la estrategia con Gemini: {e}"}}

# --- 3. Output Node ---
def present_output_node(state: State) -> Dict[str, str]:
    """
    Formatea la estrategia de apuestas para el usuario.
    """
    # print("\n--- Nodo: Presentar Salida ---")
    recommendations = state.get("betting_recommendation")
    
    # Si el resultado es un diccionario, lo devolvemos directamente como JSON
    if isinstance(recommendations, dict):
        if "error" in recommendations:
            return {"output": f"Error: {recommendations['error']}"}
        else:
            # Convertir el diccionario a una cadena JSON bien formateada
            json_output = json.dumps(recommendations, indent=2)
            return {"output": json_output}
    else:
        return {"output": "No se generaron recomendaciones de apuestas."}

# --- LangGraph Setup ---
builder = StateGraph(state_schema=State)
# builder.add_node("user_input", user_input_node)  # Elimina este nodo
builder.add_node("fetch_data_from_api", fetch_data_from_api_node)
builder.add_node("reasoning", reasoning_node)
builder.add_node("present_output", present_output_node)

# builder.set_entry_point("user_input")
builder.set_entry_point("fetch_data_from_api")
builder.add_edge("fetch_data_from_api", "reasoning")
builder.add_edge("reasoning", "present_output")
builder.add_edge("present_output", END)
graph = builder.compile()

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    betting_amount = data.get("betting_amount", 0.0)
    initial_state_inputs = {
        "message": HumanMessage(content=""),
        "betting_amount": betting_amount,
        "current_date": datetime.date.today(),
    }
    final_state = graph.invoke(initial_state_inputs)
    # El output ya es un JSON serializable
    return jsonify(final_state["output"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)

