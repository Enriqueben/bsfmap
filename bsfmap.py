from flask import Flask, request
import folium
from folium import Map, Marker, TileLayer, Icon
import sqlite3


app = Flask(__name__)
DATABASE = 'comentarios1.db'

def create_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ubicaciones
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nombre TEXT,
                 latitud FLOAT,
                 longitud FLOAT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comentarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ubicacion_id INTEGER,
                 comentario TEXT,
                 FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones (id))''')
    conn.commit()
    conn.close()

def leer_ubicaciones():
    ubicaciones = []
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, nombre, latitud, longitud FROM ubicaciones")
    rows = c.fetchall()
    for row in rows:
        ubicaciones.append(row)
    conn.close()
    return ubicaciones

def leer_comentarios(ubicacion_id):
    comentarios = []
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, comentario FROM comentarios WHERE ubicacion_id=?", (ubicacion_id,))
    rows = c.fetchall()
    for row in rows:
        comentarios.append(row)
    conn.close()
    return comentarios
app.static_folder = 'static'
@app.route('/')
def mapa():
    create_database()

    mapa = folium.Map(location=[-25.23695541510235, -57.567547239571], zoom_start=16)

    TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
              attr='Esri', 
              name='Esri World Imagery',
              overlay=True).add_to(mapa)

    ubicaciones = leer_ubicaciones()

    for ubicacion in ubicaciones:
        ubicacion_id = ubicacion[0]
        nombre = ubicacion[1]
        latitud = ubicacion[2]
        longitud = ubicacion[3]
        html_formulario = f"""
            <form action="/comentarios" method="post">
                <input type="hidden" name="ubicacion_id" value="{ubicacion_id}">
                <input type="hidden" name="latitud" value="{latitud}">
                <input type="hidden" name="longitud" value="{longitud}">
                <textarea name="comentario" placeholder="Ingrese su comentario"></textarea>
                <button type="submit" class="button">Enviar</button>
            </form>
        """
        comentarios = leer_comentarios(ubicacion_id)
        comentarios_html = ''
        for comentario in comentarios:
            comentario_id = comentario[0]
            comentario_texto = comentario[1]
            comentarios_html += f'<div>{comentario_texto} [<a href="/editar/{comentario_id}" class="button">Editar</a>]</div>'
        popup_content = f'{nombre}<br>{html_formulario}<br>Comentarios:<br>{comentarios_html}'
        folium.Marker(
            location=[latitud, longitud],
            popup=popup_content,
            icon=folium.Icon(color='orange', icon='home')
        ).add_to(mapa)

    html_mapa = mapa._repr_html_()
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa de casas bsf</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" type="text/css" href="/static/styles.css">
            {folium.Map().get_root().header.render()}
        </head>
        <body>
            <div>{html_mapa}</div>
        </body>
        </html>
    """

@app.route('/comentarios', methods=['POST'])
def comentarios():
    ubicacion_id = request.form.get('ubicacion_id')
    latitud = request.form.get('latitud')
    longitud = request.form.get('longitud')
    comentario = request.form.get('comentario')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO comentarios (ubicacion_id, comentario) VALUES (?, ?)",
              (ubicacion_id, comentario))
    conn.commit()
    conn.close()

    return 'Comentario enviado exitosamente'

@app.route('/editar/<comentario_id>', methods=['GET', 'POST'])
def editar_comentario(comentario_id):
    if request.method == 'POST':
        nuevo_comentario = request.form.get('nuevo_comentario')

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("UPDATE comentarios SET comentario=? WHERE id=?", (nuevo_comentario, comentario_id))
        conn.commit()
        conn.close()

        return 'Comentario editado exitosamente'
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT comentario FROM comentarios WHERE id=?", (comentario_id,))
    comentario_texto = c.fetchone()[0]
    conn.close()

    return f'''
        <form action="/editar/{comentario_id}" method="post">
            <textarea name="nuevo_comentario">{comentario_texto}</textarea>
            <button type="submit">Guardar</button>
        </form>
    '''

if __name__ == '__main__':
    app.run()
