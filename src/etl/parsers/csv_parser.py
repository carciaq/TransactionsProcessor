from .base import Parser
from collections.abc import Iterator
import csv
from etl.domain.transaccion import Transaccion
from etl.domain.dinero import Dinero
from decimal import Decimal
import decimal
from datetime import datetime
from etl.exceptions.exceptions import RowError, FormatError
from etl.exceptions.logger import logger

class CSVParser(Parser):
    
    def parse(self, source: str) -> Iterator[Transaccion]:
        try:
            with open(source) as data:
                reader = csv.DictReader(data)
                for i, row in enumerate(reader, start=1):
                    try:
                        yield Transaccion(
                            id=row["id"].strip(),
                            fecha=datetime.strptime(row["fecha"].strip(), "%Y-%m-%d %H:%M:%S"),
                            comercio_id=row["comercio_id"].strip(),
                            comercio_nombre=row["comercio_nombre"].strip().lower(),
                            cliente_id=row["cliente_id"].strip(),
                            ciudad=row["ciudad"].strip(),
                            valor=Dinero(monto=Decimal(row["monto"].strip()), moneda=row["moneda"].strip().upper()),
                            estado=row["estado"].strip().lower(),
                            canal=row["canal"].strip().lower()
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(RowError(row_number=i, row_data=row, source=source, original_exception=e))
                    except decimal.InvalidOperation as e:
                        logger.warning(FormatError(row_number=i, row_data=row, source=source, original_exception="Valor de monto no es un numero valido"))
        
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {source}. Error: {e}")
            raise