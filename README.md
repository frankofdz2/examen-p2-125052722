# DataMart — Examen Segundo Parcial

**Alumno:** Franko Ignacio Del Toro Fernández  
**Matrícula:** 125052722  
**Materia:** Manejo Masivo de Datos (Big Data)  
**Docente:** Javier Moya  
**Modalidad:** Individual

## Pregunta de negocio

La matrícula termina en **2**: *ticket promedio (ingreso promedio por registro) por tienda*.

Se calcula como `SUM(cantidad * precio_unitario) / COUNT(registros)` para cada tienda. Los importes se acumulan en centavos enteros para evitar diferencias de coma flotante; el promedio se guarda con seis decimales.

## Requisitos

Docker Engine con Compose v2, Python 3 en el anfitrión, espacio libre suficiente para el CSV, imágenes y salida, y conexión a Internet durante la primera construcción. No se requiere instalar Hadoop ni PostgreSQL en el anfitrión.

## Reproducción

1. Copiar `.env.example` a `.env` y reemplazar la contraseña de ejemplo por una contraseña local segura. Nunca subir `.env`.
2. Generar el dataset exacto del examen con `python generar_dataset.py 125052722`. El script original crea `ventas_125052722.csv` en el directorio actual.
3. Mover `ventas_125052722.csv` a la carpeta `datos/` (en PowerShell: `Move-Item ventas_125052722.csv datos/`). No subir el CSV a Git.
4. Ejecutar **`docker compose up --build`** desde la raíz. Este único comando construye los servicios, inicia PostgreSQL, levanta SSH, procesa el CSV con Hadoop, mide el secuencial, compara resultados y carga la tabla. La API queda disponible durante y después del procesamiento. La primera ejecución puede tardar por la descarga de Hadoop y el procesamiento de cinco millones de registros.
5. Consultar `http://localhost:8000/health`, `http://localhost:8000/resultados` y `http://localhost:8000/resultados/T001` (o el puerto configurado en `.env`). Antes de terminar el procesamiento, la lista puede estar vacía.

## Servicios y persistencia

- `hadoop`: Debian Bookworm, OpenJDK 17, Python 3, Hadoop 3.3.6 standalone y OpenSSH Server.
- `db`: PostgreSQL 16, volumen nombrado `postgres_data`.
- `api`: Flask con Gunicorn y conexión a PostgreSQL por el hostname `db`.
- Red privada `datamart` definida en Compose. Volumen compartido `ssh_keys` para las llaves generadas al iniciar Hadoop. CSV montado en `/data/input` como solo lectura.

## Comandos de verificación

```sh
docker compose exec hadoop hadoop version
docker compose exec hadoop ssh -o BatchMode=yes localhost 'echo SSH_LOCAL_OK'
docker compose exec api sh -lc 'ssh -i /shared-ssh/id_ed25519 -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@hadoop hostname'
docker compose exec db psql -U datamart -d datamart -c 'SELECT * FROM resultados ORDER BY tienda LIMIT 5;'
docker compose logs hadoop
```

La última consulta supone que no cambiaste `POSTGRES_USER` ni `POSTGRES_DB`.

## Hadoop Streaming

El mapper ignora el encabezado y filas incorrectas, y emite `tienda\tcentavos\t1`. Hadoop agrupa por tienda. El reducer suma centavos y contadores y escribe `tienda\tpromedio`. La salida real se guarda en `salida/resultado/part-00000`. Los registros se cargan mediante `scripts/cargar_resultados.py` con `INSERT ... ON CONFLICT DO UPDATE`.

## Comparativa de rendimiento

Los tiempos se generan automáticamente en `salida/comparativa.json`. **Completar después de ejecutar el examen:**

| Método | Tiempo real |
|---|---|
| Hadoop Streaming | Pendiente de medición |
| Python secuencial | Pendiente de medición |
| ¿Coinciden? | Pendiente de verificación |

La comparación es exacta a seis decimales y el pipeline se detiene si hay discrepancias. En una máquina, Hadoop Streaming puede ser más lento porque inicia una JVM y procesos auxiliares, realiza operaciones de agrupación y ordenamiento y escribe archivos intermedios; un recorrido secuencial puede resolver esta agregación con menos sobrecarga. Hadoop destaca cuando los datos y el trabajo se distribuyen entre varios nodos.

## API y CRUD

- `GET /health`: estado de conexión a PostgreSQL.
- `GET /resultados`: lista de promedios por tienda.
- `GET /resultados/T001`: promedio de una tienda.
- `POST /resultados`: crea un registro con JSON `{"tienda":"T999","ticket_promedio":"150.250000"}`.
- `PUT /resultados/T999`: modifica el promedio de esa tienda con JSON `{"ticket_promedio":"180.000000"}`.
- `DELETE /resultados/T999`: elimina el registro.

Ejemplo de escritura (PowerShell):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/resultados -ContentType 'application/json' -Body '{"tienda":"T999","ticket_promedio":"150.250000"}'
```

## Persistencia

Para demostrar persistencia sin recalcular, ejecutar `docker compose down` y después `docker compose up -d db api`. La tabla permanece porque el volumen nombrado no se elimina. Consultar de nuevo `/resultados`. Para reiniciar el pipeline completo, `docker compose up --build` también vuelve a procesar y actualizar los registros.

`docker compose down -v` **sí elimina** el volumen de PostgreSQL y las llaves SSH generadas. El CSV original no se elimina porque está montado desde el anfitrión.

## Evidencias reales por adjuntar

Guardar en `evidencias/` capturas propias con fecha de: `hadoop version`, `ssh localhost`, `ssh root@hadoop` desde API, salida de `part-00000`, `comparativa.json`, respuesta de `/resultados`, prueba POST y persistencia tras reinicio. No se incluyen capturas simuladas.

## Teoría y defensa

Ver `TEORIA.md` y `DEFENSA_ORAL.md`.

## Entrega

Repositorio Git con código y evidencias reales, sin CSV, sin `.env` ni contraseñas. El archivo `.env.example` solo contiene valores de ejemplo.

## Resultados reales de ejecución

Matrícula: 125052722
Pregunta: Ticket promedio por registro de venta y tienda.

| Método | Tiempo |
|---|---:|
| Hadoop MapReduce | 80.400 segundos |
| Python secuencial | 33.685 segundos |

Se procesaron 5,000,000 de registros y se obtuvieron resultados para 14 tiendas. Ambos métodos coincidieron.

Python secuencial fue aproximadamente 2.39 veces más rápido. Hadoop ejecutado en modo standalone introduce una sobrecarga de inicialización y procesamiento que no se compensa al trabajar con este volumen de datos en un solo equipo. Hadoop puede resultar más conveniente al procesar datasets mayores en un clúster distribuido.

La API devolvió 14 registros después de detener y volver a levantar los servicios con Docker Compose, demostrando la persistencia de PostgreSQL.

