from typing import Protocol 

class Exportador(Protocol):
    def exportar(self, reporte : dict) -> None:
        pass