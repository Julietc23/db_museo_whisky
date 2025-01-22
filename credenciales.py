import sqlite3

# Crear la base de datos SQLite (si no existe)
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Crear la tabla de usuarios (si no existe)
c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        contraseña TEXT NOT NULL
    )
''')

# Insertar un usuario de ejemplo (esto solo se hace una vez)
c.execute("INSERT INTO usuarios (usuario, contraseña) VALUES ('admin123', 'admin123')")
conn.commit()

# Cerrar la conexión
conn.close()



import streamlit as st
import sqlite3
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar la clave API de OpenAI
openai.api_key = os.getenv("API_KEY")
# Función para verificar el usuario y la contraseña desde la base de datos SQLite
import sqlite3
import shutil
from datetime import datetime

def verificar_usuario(username, password):
    # Conectar a la base de datos
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    
    # Verificar usuario
    c.execute("SELECT * FROM usuarios WHERE usuario = ? AND contraseña = ?", (username, password))
    user = c.fetchone()  # Obtiene el primer registro que coincida
    
    # Hacer backup si el usuario fue encontrado
    if user:
        backup_db()

    conn.close()
    return user








   


#SE AGREGA ESTA FUNCION 22/01/2025
#DEBE ESTAR EN LA EJECUCION DE LA CONSULTA DE LA DB
def backup_db():
    # Obtener la fecha y hora actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Crear el nombre del archivo de respaldo
    backup_filename = f"usuarios_backup_{timestamp}.db"
    # Hacer una copia del archivo de la base de datos
    shutil.copyfile('usuarios.db', backup_filename)
    print(f"Backup realizado: {backup_filename}")

# Función para interactuar con OpenAI y generar una respuesta
def obtener_respuesta_openai(pregunta):
       mensaje = [
        {
            'role': 'system',
            'content': f"""Eres un asistente experto que responde preguntas.            
            
            Si el mensaje no incluye una pregunta, debes presentarte."""
        },
        {'role': 'user', 'content': pregunta}
    ]
       response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=mensaje,
        temperature=0
    )
       return response['choices'][0]['message']['content']

#    response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=mensaje,
#         temperature=0
#     )
#     return response['choices'][0]['message']['content']




# Interfaz de inicio de sesión
def login():
    st.title("Inicio de sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if verificar_usuario(username, password):
        # if crear_usuario(username, password):
            st.session_state.authenticated = True
            st.success("¡Acceso concedido!")
            return True
        else:
            st.session_state.authenticated = False
            st.error("Usuario o contraseña incorrectos")
            return False

# Verificar si el usuario está autenticado
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Si el usuario no está autenticado, mostrar la pantalla de inicio de sesión
if not st.session_state.authenticated:
    if not login():
        st.stop()  # Detiene la ejecución del resto de la aplicación si no está autenticado

# Si el usuario está autenticado, mostrar el contenido de la aplicación
if st.session_state.authenticated:
    st.title("Bienvenido a la aplicación")
    st.write("Este es el contenido protegido por autenticación.")

    # Aquí puedes agregar la funcionalidad con OpenAI
    st.subheader("Pregunta a Base de Datos de Whisky")
    pregunta = st.text_input("Escribe tu pregunta para OpenAI")
    
    if pregunta:
        respuesta = obtener_respuesta_openai(pregunta)
        st.write("Respuesta de la base de datos:")
        st.write(respuesta)

   
