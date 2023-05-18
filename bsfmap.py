from flask import Flask, render_template
from folium import Map, Marker, TileLayer, Icon
import folium

app = Flask(__name__)

def leer_ubicaciones():
    ubicaciones = []
    with open("ubicaciones.txt", "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            if len(datos) == 3:
                nombre = datos[0].strip()
                latitud = float(datos[1].strip())
                longitud = float(datos[2].strip())
                ubicaciones.append((nombre, latitud, longitud))
    return ubicaciones

@app.route('/')
def mapa():
    # Crear mapa centrado en una ubicación concreta
    mapa = folium.Map(location=[-25.23695541510235, -57.567547239571], zoom_start=16)

    TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
              attr='Esri', 
              name='Esri World Imagery',
              overlay=True).add_to(mapa)

    # Leer ubicaciones desde el archivo plano
    ubicaciones = leer_ubicaciones()

    # Iterar sobre la lista de ubicaciones para crear marcadores en cada una
    for ubicacion in ubicaciones:
        nombre = ubicacion[0]
        latitud = ubicacion[1]
        longitud = ubicacion[2]
        folium.Marker(
            location=[latitud, longitud],
            popup=nombre,
            icon=folium.Icon(color='orange', icon='home')
        ).add_to(mapa)

    # Renderizar mapa en HTML
    html_mapa = mapa._repr_html_()
    # Devolver HTML con el mapa
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa de casas bsf</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {folium.Map().get_root().header.render()}
        </head>
        <body>
            <div>{html_mapa}</div>
        </body>
        </html>
    """

if __name__ == '__main__':
    app.run()
