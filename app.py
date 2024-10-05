from flask import Flask, request, jsonify
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Función para calcular la distancia usando la fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
    R = 6371.0

    # Convertir grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distancia
    distancia = R * c
    return distancia

@app.route('/obtener_eventos', methods=['POST'])
def obtener_eventos():
    data = request.json
    mi_lat = data['lat']
    mi_lon = data['lon']

    # URL de la API de EONET
    url = "https://eonet.gsfc.nasa.gov/api/v2.1/events"

    # Realizar la solicitud GET
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        eventos_cercanos = []
        data = response.json()

        # Recorrer los eventos y calcular la distancia
        for evento in data['events']:
            # Verificar si el evento tiene la clave 'geometries'
            if 'geometries' in evento and evento['geometries']:
                # Usar la primera geometría (que es la posición actual del evento)
                lat_evento = evento['geometries'][0]['coordinates'][1]
                lon_evento = evento['geometries'][0]['coordinates'][0]

                # Calcular la distancia entre tu ubicación y el evento
                distancia = calcular_distancia(mi_lat, mi_lon, lat_evento, lon_evento)

                if distancia <= 10000:  # Si el evento está dentro de los 200 km
                    eventos_cercanos.append({
                        "titulo": evento['title'],
                        "distancia_km": distancia,
                        "ubicacion": (lat_evento, lon_evento)
                    })

        # Devolver los eventos cercanos
        return jsonify(eventos_cercanos), 200
    else:
        return jsonify({"error": f"Error en la solicitud: {response.status_code}"}), 500

if __name__ == '__main__':
    app.run(debug=True)