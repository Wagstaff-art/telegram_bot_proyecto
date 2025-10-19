import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")

def obtener_clima(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&lang=es&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        # Si hay error, lo mostramos
        if response.status_code != 200 or "main" not in data:
            mensaje_error = data.get("message", "Ciudad no encontrada.")
            return f"⚠️ Error: {mensaje_error.capitalize()}"

        nombre_ciudad = data["name"]
        pais = data["sys"]["country"]
        temperatura = data["main"]["temp"]
        descripcion = data["weather"][0]["description"]
        humedad = data["main"]["humidity"]
        icono = data["weather"][0]["icon"]

        return (
            f"📍 *{nombre_ciudad}, {pais}*\n"
            f"🌡️ Temperatura: {temperatura}°C\n"
            f"📋 Condición: {descripcion.capitalize()}\n"
            f"💧 Humedad: {humedad}%\n"
            f"[🌥️ Ver icono](http://openweathermap.org/img/wn/{icono}@2x.png)"
        )

    except Exception as e:
        return f"❌ Error inesperado: {e}"
