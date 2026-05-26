from etl.exceptions.exceptions import DuplicateIDError
from etl.parsers.base import Parser
from etl.analytics.analista import Analista
from etl.export import Exportador
from dataclasses import asdict
import logging


class ProcesadorTransacciones:
    def __init__(
        self,
        parser: Parser,
        analista: Analista,
        exportadores: list[Exportador],
        tasas: dict[str, float]
    ) -> None:
        
        self.parser = parser
        self.analista = analista
        self.exportadores = exportadores
        self.tasas = tasas    
        self.procesadas = 0
    
    
    def procesar(self, source: str) -> int:
        """
        1. Lee transacciones con el parser (streaming).
        2. Convierte a COP las que no lo están.
        3. Calcula todas las métricas con el analista.
        4. Construye un reporte (dict).
        5. Invoca a cada exportador con el reporte.
        6. Devuelve el reporte para que el caller pueda inspeccionarlo.
        """
        ids_vistos: set[str] = set()
        for i, transaccion in enumerate(self.parser.parse(source), start=1):
            if transaccion.id in ids_vistos:
                try:
                    raise DuplicateIDError(row_number=i, row_data=asdict(transaccion), source=source)
                except DuplicateIDError as e:
                    logging.warning("ID duplicado encontrado", exc_info=True)
            else: self.procesadas += 1
            ids_vistos.add(transaccion.id)
        
        return 0