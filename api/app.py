import os
from decimal import Decimal, InvalidOperation
from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import errors

app = Flask(__name__)

def conectar():
    return psycopg2.connect(host=os.environ.get("POSTGRES_HOST", "db"),
        dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"])

def preparar():
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS resultados (
                tienda VARCHAR(32) PRIMARY KEY,
                ticket_promedio NUMERIC(18,6) NOT NULL CHECK (ticket_promedio >= 0))""")

def serializar(fila):
    return {"tienda": fila[0], "ticket_promedio": str(fila[1])}

@app.get("/health")
def health():
    try:
        with conectar() as con:
            with con.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify(estado="ok", base_de_datos="conectada")
    except psycopg2.Error:
        return jsonify(estado="error", base_de_datos="no disponible"), 503

@app.get("/resultados")
def resultados():
    preparar()
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("SELECT tienda, ticket_promedio FROM resultados ORDER BY tienda")
            filas = cur.fetchall()
    return jsonify([serializar(f) for f in filas])

@app.get("/resultados/<tienda>")
def resultado(tienda):
    preparar()
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("SELECT tienda, ticket_promedio FROM resultados WHERE tienda=%s", (tienda,))
            fila = cur.fetchone()
    if fila is None:
        return jsonify(error="Tienda no encontrada"), 404
    return jsonify(serializar(fila))

@app.post("/resultados")
def crear():
    datos = request.get_json(silent=True) or {}
    tienda = datos.get("tienda")
    try:
        valor = Decimal(str(datos.get("ticket_promedio")))
        if not isinstance(tienda, str) or not tienda.strip() or len(tienda) > 32 or not valor.is_finite() or valor < 0:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        return jsonify(error="Se requiere tienda valida y ticket_promedio no negativo"), 400
    preparar()
    try:
        with conectar() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO resultados (tienda,ticket_promedio) VALUES (%s,%s) RETURNING tienda,ticket_promedio", (tienda.strip(), valor))
                fila = cur.fetchone()
        return jsonify(serializar(fila)), 201
    except errors.UniqueViolation:
        return jsonify(error="La tienda ya existe"), 409

@app.put("/resultados/<tienda>")
def actualizar(tienda):
    datos = request.get_json(silent=True) or {}
    try:
        valor = Decimal(str(datos.get("ticket_promedio")))
        if not valor.is_finite() or valor < 0:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        return jsonify(error="ticket_promedio invalido"), 400
    preparar()
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("UPDATE resultados SET ticket_promedio=%s WHERE tienda=%s RETURNING tienda,ticket_promedio", (valor, tienda))
            fila = cur.fetchone()
    return (jsonify(serializar(fila)), 200) if fila else (jsonify(error="Tienda no encontrada"), 404)

@app.delete("/resultados/<tienda>")
def eliminar(tienda):
    preparar()
    with conectar() as con:
        with con.cursor() as cur:
            cur.execute("DELETE FROM resultados WHERE tienda=%s RETURNING tienda", (tienda,))
            fila = cur.fetchone()
    return ("", 204) if fila else (jsonify(error="Tienda no encontrada"), 404)
