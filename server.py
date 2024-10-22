from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Función para conectar a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('users.db')  # Crea o abre la base de datos
    conn.row_factory = sqlite3.Row  # Permite acceder a los datos como diccionarios
    return conn

# Inicializar la base de datos y crear la tabla si no existe
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Endpoint para Home
@app.route('/')
def index():
    html_file = open("index.html", "r")
    return(html_file.read()) 

# Endpoint para Text
@app.route('/test')
def test():
    return jsonify({'message': 'test ok'})

# Endpoint para obtener todos los usuarios
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()  # Obtener todos los usuarios
    conn.close()

    return jsonify([dict(user) for user in users])  # Convertir a lista de diccionarios

# Endpoint para crear un usuario
@app.route('/api/v1/users/', methods=['POST'])
def create_user():
    data = request.json
    name = data['name']
    telefono = data['telefono']

    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, telefono) VALUES (?, ?)', (name, telefono))
    conn.commit()
    conn.close()

    response = {
        'message': 'Usuario creado exitosamente',
        'user': data
    }
    return jsonify(response), 201

# Endpoint para actualizar un usuario (PUT)
@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name')
    telefono = data.get('telefono')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    conn.execute('UPDATE users SET name = ?, telefono = ? WHERE id = ?', (name, telefono, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

# Endpoint para eliminar un usuario (DELETE)
@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Usuario eliminado exitosamente'}), 200

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos
    app.run(debug=True, port=5000)
