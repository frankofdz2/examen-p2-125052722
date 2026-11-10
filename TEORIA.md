# Parte E. Teoría

**1. Modos de Hadoop.** En standalone, Hadoop ejecuta el procesamiento en una sola máquina y usa el sistema de archivos local. En pseudo-distribuido, los demonios de Hadoop corren como procesos separados en una sola máquina, normalmente con HDFS. En el modo totalmente distribuido, los procesos se reparten entre varios servidores y utilizan HDFS para distribuir y replicar datos. HDFS se utiliza habitualmente en los dos últimos modos, no en standalone.

**2. Dataset como volumen.** El CSV se monta porque es grande y no debe incorporarse a cada versión de la imagen. Esto reduce el tamaño de la imagen y evita reconstruirla cuando cambian los datos. Además, el montaje de solo lectura impide que el procesamiento modifique el archivo original.

**3. Persistencia.** `docker compose down` elimina contenedores y la red creada, pero conserva los volúmenes nombrados, por lo que PostgreSQL mantiene sus registros. Con `docker compose down -v` también se eliminan los volúmenes nombrados del proyecto, incluido el de PostgreSQL, y se pierden sus datos almacenados ahí.

**4. Rendimiento.** MapReduce tiene costos de inicio, preparación del job, lectura y escritura intermedias y ordenamiento. Con un archivo de unos 400 MB y una sola máquina, ese costo puede superar las ventajas del paralelismo. Conviene más con datos mayores, varias máquinas, múltiples particiones y tareas que puedan ejecutarse en paralelo.

**5. Instrucciones Docker.** `CMD` indica el comando o argumentos predeterminados, que pueden reemplazarse al ejecutar el contenedor. `ENTRYPOINT` define el ejecutable principal; `CMD` puede proporcionarle argumentos. `COPY` copia archivos al construir la imagen. `ADD` también permite extraer automáticamente archivos tar locales y obtener recursos desde URL, pero `COPY` suele ser más claro para copias sencillas.
