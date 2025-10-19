import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Cargar variables de entorno
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Instancia del modelo Gemini (ajusta si usas otro)
modelo = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-pro",  # modelo que sí funciona según tu lista
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True
)

# Función para responder
def responder_gemini(mensaje_usuario: str) -> str:
    try:
        respuesta = modelo.invoke([
            HumanMessage(content=mensaje_usuario)
        ])
        return respuesta.content.strip()
    except Exception as e:
        return "❌ Error al contactar con Gemini. Intenta de nuevo más tarde."
