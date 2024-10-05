from main import Flask, request, jsonify
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Función para calcular la distancia usando la fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = R * c
    return distancia

@app.route('/tu-ruta-python', methods=['POST'])
def recibir_ubicacion():
    data = request.get_json()
    mi_lat = data['latitude']
    mi_lon = data['longitude']

    # URL de la API de EONET
    url = "https://eonet.gsfc.nasa.gov/api/v2.1/events"
    response = requests.get(url)

    if response.status_code == 200:
        eventos_cercanos = []
        data = response.json()

        for evento in data['events']:
            if 'geometries' in evento and evento['geometries']:
                lat_evento = evento['geometries'][0]['coordinates'][1]
                lon_evento = evento['geometries'][0]['coordinates'][0]

                # Calcular la distancia entre la ubicación y el evento
                distancia = calcular_distancia(mi_lat, mi_lon, lat_evento, lon_evento)

                if distancia <= 200:  # Si el evento está dentro de los 200 km
                    eventos_cercanos.append({
                        "titulo": evento['title'],
                        "distancia_km": distancia,
                        "ubicacion": (lat_evento, lon_evento)
                    })

        return jsonify(eventos_cercanos)
    else:
        return jsonify({"error": "Error al obtener eventos"}), 500

if __name__ == '__main__':
    app.run(debug=True)
