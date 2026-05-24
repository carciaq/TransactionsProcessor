import logging

from .base import Parser
from collections.abc import Iterator
import csv
from etl.domain.transaccion import Transaccion
from etl.domain.dinero import Dinero
from decimal import Decimal
from datetime import datetime

class CSVParser(Parser):
    
    def parse(self, source: str) -> Iterator[Transaccion]:
        with open(source) as data:
            reader = csv.DictReader(data)
            for i,row in enumerate(reader):
                
                try:
                    yield Transaccion(
                    id=row['id'].strip(),
                    fecha=datetime.strptime(row['fecha'], '%Y-%m-%d %H:%M:%S'),
                    comercio_id=row['comercio_id'].strip(),
                    comercio_nombre=row['comercio_nombre'].strip().lower(),
                    cliente_id=row['cliente_id'].strip(),
                    ciudad=row['ciudad'].strip(),
                    valor=Dinero(monto=Decimal(row['monto']), moneda=row['moneda'].strip().upper()),
                    estado=row['estado'].strip().lower(),
                    canal=row['canal'].lower().strip()
                )
                except Exception as e:
                    logging.warning(f"Error al parsear la fila {i + 1} ({row}): {e}")