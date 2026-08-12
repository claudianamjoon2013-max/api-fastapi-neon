import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def crear_tablas():
    conn = get_connection()
    cur = conn.cursor()

    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE
        );
    """)

    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            precio NUMERIC(10,2) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categoria_id INTEGER NOT NULL,
            CONSTRAINT fk_categoria
                FOREIGN KEY (categoria_id) 
                REFERENCES categorias (id) 
                ON DELETE RESTRICT
        );
    """)

  
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        );
    """)

    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            documento INTEGER PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL,
            cargo VARCHAR(30) NOT NULL,
            salario FLOAT NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

crear_tabla_productos = crear_tablas