# Defensa oral — preparación

**Explicación del pipeline (30 segundos).** Generé cinco millones de ventas con la matrícula como semilla. El mapper convierte cada venta en un par tienda e ingreso en centavos, acompañado de un contador. Hadoop agrupa por tienda y el reducer suma los ingresos y los contadores para obtener el promedio. Después verifico el resultado con un programa secuencial, cargo los promedios a PostgreSQL y los consulto por la API.

**Cambiar puerto.** Editar `API_PORT=8001` en `.env` y ejecutar `docker compose up -d --build api`; consultar `http://localhost:8001/resultados`. El puerto interno sigue siendo 8000.

**Cambiar suma por promedio.** El mapper ya produce `(ingreso_en_centavos, 1)` y el reducer calcula `suma / conteo`; para sumar solamente se elimina la división por el conteo y se convierte la suma de centavos a pesos. Si se cambia la agregación también hay que actualizar la comparación y la tabla.

**Filtrar un mes.** En mapper.py, antes de emitir, comprobar `row[1][0:7] == "2025-06"`. El programa secuencial debe usar el mismo filtro para comparar correctamente.

**Borrar volumen y recargar.** Ejecutar `docker compose down -v` y después `docker compose up --build`. Atención: también se borran las llaves SSH generadas y se regeneran; los archivos CSV montados en el host permanecen. El pipeline reconstruye la tabla desde los resultados.

**Dockerfile.** FROM define Debian, RUN instala Java/Python/SSH/Hadoop, ENV configura rutas, COPY incorpora el código y ENTRYPOINT inicia SSH y ejecuta el pipeline.

**Diagnóstico.** `docker compose ps`, `docker compose logs hadoop`, `docker compose logs api`, `docker compose exec hadoop hadoop version`, `docker compose exec db pg_isready -U datamart -d datamart`.

**SSH desde API.** `docker compose exec api sh -lc 'ssh -i /shared-ssh/id_ed25519 -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@hadoop hostname'`.

**Nota.** Las cifras de rendimiento deben leerse de `salida/comparativa.json`, nunca inventarse.
