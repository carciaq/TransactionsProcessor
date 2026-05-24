from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from etl.domain.dinero import Dinero

@dataclass(frozen=True, slots=True)
class Transaccion:
    id: str
    fecha: datetime 
    comercio_id: str
    comercio_nombre: str
    cliente_id: str
    ciudad: str
    valor: Dinero
    estado: str
    canal: str