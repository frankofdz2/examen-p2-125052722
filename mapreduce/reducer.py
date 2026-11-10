import sys
from decimal import Decimal

def emitir(tienda, total, cantidad):
    if tienda is not None and cantidad:
        promedio = (Decimal(total) / Decimal(cantidad) / 100).quantize(Decimal("0.000001"))
        print(f"{tienda}\t{promedio}")

actual = None
total = 0
cantidad = 0
for linea in sys.stdin:
    try:
        tienda, centavos, registros = linea.rstrip("\n").split("\t")
        ingreso = int(centavos)
        n = int(registros)
    except ValueError:
        continue
    if actual is not None and tienda != actual:
        emitir(actual, total, cantidad)
        total = cantidad = 0
    actual = tienda
    total += ingreso
    cantidad += n
emitir(actual, total, cantidad)
