import json
import os
from pathlib import Path
import subprocess
import sys
import time
from decimal import Decimal

entrada = Path(sys.argv[1])
carpeta = Path(sys.argv[2])
carpeta.mkdir(parents=True, exist_ok=True)
resultado = carpeta / "resultado"
if resultado.exists():
    import shutil
    shutil.rmtree(resultado)
mapper = "/opt/datamart/mapreduce/mapper.py"
reducer = "/opt/datamart/mapreduce/reducer.py"
jar = next(Path(os.environ["HADOOP_HOME"]).glob("share/hadoop/tools/lib/hadoop-streaming-*.jar"))
comando = ["hadoop", "jar", str(jar), "-D", "mapreduce.framework.name=local",
    "-D", "mapreduce.job.reduces=1", "-files", f"{mapper},{reducer}",
    "-input", str(entrada), "-output", str(resultado),
    "-mapper", "python3 mapper.py", "-reducer", "python3 reducer.py"]
print("INICIANDO_HADOOP_STREAMING", flush=True)
inicio = time.perf_counter()
with (carpeta / "hadoop.log").open("w") as log:
    proceso = subprocess.run(comando, stdout=log, stderr=subprocess.STDOUT)
tiempo_hadoop = time.perf_counter() - inicio
if proceso.returncode:
    print("ERROR_HADOOP: revisar salida/hadoop.log", flush=True)
    sys.exit(proceso.returncode)
print(f"HADOOP_SEGUNDOS={tiempo_hadoop:.3f}", flush=True)
secuencial = subprocess.run(["python3", "/opt/datamart/mapreduce/secuencial.py",
    str(entrada), str(carpeta / "secuencial.json")], capture_output=True, text=True, check=True)
print(secuencial.stdout, flush=True)
resultado_sec = json.loads((carpeta / "secuencial.json").read_text())
resultado_hadoop = {}
with (resultado / "part-00000").open() as f:
    for linea in f:
        tienda, promedio = linea.rstrip("\n").split("\t")
        resultado_hadoop[tienda] = promedio
coincide = {k: Decimal(v) for k,v in resultado_sec.items()} == {k: Decimal(v) for k,v in resultado_hadoop.items()}
reporte = {"matricula": "125052722", "hadoop_segundos": round(tiempo_hadoop,3),
    "secuencial_segundos": float(secuencial.stdout.split("SECUENCIAL_SEGUNDOS=")[1].splitlines()[0]),
    "coinciden": coincide, "tiendas": len(resultado_hadoop)}
(carpeta / "comparativa.json").write_text(json.dumps(reporte,indent=2))
print("COMPARATIVA="+json.dumps(reporte), flush=True)
if not coincide:
    sys.exit("ERROR: resultados distintos. No se cargaran a la base de datos.")
subprocess.run(["python3", "/opt/datamart/scripts/cargar_resultados.py",
    str(resultado / "part-00000")], check=True)
print("PIPELINE_OK", flush=True)
