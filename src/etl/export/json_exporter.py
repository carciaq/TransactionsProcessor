import json
from typing import Any
from decimal import Decimal
from dataclasses import is_dataclass, asdict


class ExportadorJSON:
    
    def __init__(self, archivo_salida: str) -> None:
        self.archivo_salida = archivo_salida

    def _normalizar(self, valor: Any) -> Any:
        if isinstance(valor, set):
            return sorted(valor)
        
        if hasattr(valor, 'monto') and hasattr(valor, 'moneda'):
            return str(valor)
        
        if is_dataclass(valor):
            return self._normalizar(asdict(valor))
        
        if isinstance(valor, Decimal):
            return str(valor)
        if isinstance(valor, dict):
            return {clave: self._normalizar(contenido) for clave, contenido in valor.items()}
        if isinstance(valor, list) or isinstance(valor, tuple):
            return [self._normalizar(contenido) for contenido in valor]
        return valor

    def exportar(self, reporte: dict) -> None:
        reporte_normalizado = self._normalizar(reporte)
        with open(self.archivo_salida, 'w', encoding='utf-8') as archivo:
            json.dump(reporte_normalizado, archivo, indent=4, ensure_ascii=False)


    