import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

for line in sys.stdin:
    try:
        row = next(csv.reader([line]))
        if len(row) != 8 or row[0].strip().lower() == "id":
            continue
        tienda = row[2].strip()
        if not tienda or "\t" in tienda or "\n" in tienda:
            continue
        cantidad = int(row[5])
        precio = Decimal(row[6])
        if cantidad <= 0 or precio < 0 or not precio.is_finite():
            continue
        centavos = int((precio * cantidad * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        print(f"{tienda}\t{centavos}\t1")
    except (ValueError, InvalidOperation, csv.Error, IndexError, StopIteration):
        continue
