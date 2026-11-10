import csv
import json
import sys
import time
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ruta = Path(sys.argv[1])
salida = Path(sys.argv[2])
acumulados = defaultdict(lambda: [0, 0])
inicio = time.perf_counter()
with ruta.open(newline="", encoding="utf-8") as archivo:
    lector = csv.reader(archivo)
    for fila in lector:
        try:
            if len(fila) != 8 or fila[0].strip().lower() == "id":
                continue
            tienda = fila[2].strip()
            if not tienda or "\t" in tienda or "\n" in tienda:
                continue
            unidades = int(fila[5]); precio = Decimal(fila[6])
            if unidades <= 0 or precio < 0 or not precio.is_finite():
                continue
            centavos = int(precio * unidades * 100)
            acumulados[tienda][0] += centavos
            acumulados[tienda][1] += 1
        except (ValueError, InvalidOperation, csv.Error, IndexError):
            continue
resultado = {t: str((Decimal(s) / Decimal(n) / 100).quantize(Decimal("0.000001")))
             for t, (s, n) in sorted(acumulados.items()) if n}
salida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"SECUENCIAL_SEGUNDOS={time.perf_counter()-inicio:.3f}")
print(f"TIENDAS={len(resultado)}")
