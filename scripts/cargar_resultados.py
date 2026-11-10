import os
import sys
from decimal import Decimal
import psycopg2

archivo = sys.argv[1]
conexion = psycopg2.connect(host=os.environ.get("POSTGRES_HOST", "db"),
    dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"])
with conexion:
    with conexion.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS resultados (
            tienda VARCHAR(32) PRIMARY KEY,
            ticket_promedio NUMERIC(18,6) NOT NULL CHECK (ticket_promedio >= 0)
        )""")
        with open(archivo, encoding="utf-8") as entrada:
            for linea in entrada:
                if not linea.strip():
                    continue
                tienda, promedio = linea.rstrip("\n").split("\t")
                cursor.execute("""INSERT INTO resultados (tienda, ticket_promedio)
                    VALUES (%s, %s) ON CONFLICT (tienda)
                    DO UPDATE SET ticket_promedio=EXCLUDED.ticket_promedio""",
                    (tienda, Decimal(promedio)))
        cursor.execute("SELECT COUNT(*) FROM resultados")
        print("FILAS_EN_POSTGRESQL=", cursor.fetchone()[0])
conexion.close()
