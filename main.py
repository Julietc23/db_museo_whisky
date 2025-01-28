import streamlit as st
import sqlite3
import openai
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Carga de variables
#load_dotenv()

openai.api_key = st.secrets["API_KEY"]

# Configurar la clave API de OpenAI
#openai.api_key = os.getenv("API_KEY")

# Función para verificar el usuario y la contraseña desde la base de datos SQLite 
def verificar_usuario(username, password):
    # Conectar a la base de datos
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    
    # Verificar usuario
    c.execute("SELECT * FROM usuarios WHERE usuario = ? AND contraseña = ?", (username, password))
    user = c.fetchone()  # Obtiene el primer registro que coincida
    
    # Hacer backup si el usuario fue encontrado
    if user:
        backup_db()

    conn.close()
    return user

# Creación de backup
def backup_db():
    """
    Crea copias de la base de datos a un path determinado.
    """
    # Ruta de la carpeta de respaldo
    backup_folder = "backups"
    # Crear la carpeta de respaldo si no existe
    os.makedirs(backup_folder, exist_ok=True)
    # Obtener la fecha y hora actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Crear el nombre del archivo de respaldo
    backup_filename = os.path.join(backup_folder, f"main_backup_{timestamp}.db")
    # Hacer una copia del archivo de la base de datos
    shutil.copyfile('main.db', backup_filename)
    print(f"Backup realizado: {backup_filename}")

# Obtención del schema
def obtener_esquema():
    """
    Obtiene el esquema de forma dinamica directamente de la base de datos.
    Salida: str con esquema.
    """
    # Conexión
    conn = sqlite3.connect('main.db')
    c = conn.cursor()

    # Recuperación de la tabla
    c.execute("SELECT name, sql FROM sqlite_master WHERE name='productos'")
    tablas = c.fetchall()

    for _, schema in tablas:
        esquema = schema
    return f"Esquema:\n{esquema};"

# Función para interactuar con OpenAI y generar SQL
def obtener_query(pregunta):
       """
       Obtiene del modelo de OpenAI la traducción de NL a SQL.
       Entrada : str en lenguaje natural.
       Salida : str en formato SQL.
       """
       mensaje = [
        {
            'role': 'system',
            'content': f"""Eres un asistente experto que responde preguntas de lenguaje natural en SQLite3, basandose en una base de datos. 
            Si el mensaje incluye una pregunta, responde en SQLite3 y solo devuelve la consulta necesaria para responder la pregunta. 
            No devuelvas '```', ni 'sql' o 'sqlite3'. No incluyas "LIKE '%whisky%'" en tu respuesta. Solo la consulta SQL.
            Debes respetar al 100% la estructura y los nombres de la tabla en tus consultas. 
            El schema de la base de datos es: {obtener_esquema()}."""
        },
        {'role': 'user', 'content': pregunta}
    ]
       response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=mensaje,
        temperature=0
    )
       #return response.choices[0].text
       return response['choices'][0]['message']['content']

# Ejecución de la respuesta
def ejecutar_query(query):
    """
    Ejecuta la query producida por el modelo de forma directa en la base de datos.
    Entrada : str en formato SQL.
    Salida : str con resultados de la consulta.
    """
    # Conexión
    conn = sqlite3.connect('main.db')
    c = conn.cursor()

    # Ejecución de query
    c.execute(query)
    result = c.fetchall()
    conn.commit()
    conn.close()

    return result

# Función para interactuar con OpenAI y generar una respuesta coherente
def obtener_respuesta_openai(question):
       """
       Ejecuta la traducción y la query. Procesa los datos para dar una salida cordial.
        Entrada : str de consulta.
        Salida : str con respuesta de modelo.
       """
       query = obtener_query(question)
       mensaje = [
        {
            'role': 'system',
            'content': f"""Eres un asistente amable que comunica los datos obtenidos apartir de una consulta realizada a una base de datos.
            Lo unico que debes de devolver son los datos, de forma breve, coherente y amigable. No debes de realizar preguntas, ni explicaciones.
            Información relevante:
            La pregunta en lenguaje natural realizada fue: {question}.
            La respuesta en SQL: {query}.
            Tus datos serán: {ejecutar_query(query)}."""
        },
        {'role': 'user', 'content': question}
    ]
       response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=mensaje,
        temperature=0
    )
       #return response.choices[0].text
       return response['choices'][0]['message']['content']


# Interfaz de inicio de sesión
def login():
    """
    Valida y habilita el acceso a la aplicación.
    """
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
    pregunta = st.text_input("Escribe tu pregunta")
    
    if pregunta:
        respuesta = obtener_respuesta_openai(pregunta)
        st.write("Respuesta:")
        st.write(respuesta)
