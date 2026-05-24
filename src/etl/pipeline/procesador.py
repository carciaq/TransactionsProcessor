from etl.parsers.base import Parser
from etl.analytics.analista import Analista
from etl.export import Exportador


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
    
    
    
    def procesar(self, source: str) -> dict:
        """
        1. Lee transacciones con el parser (streaming).
        2. Convierte a COP las que no lo están.
        3. Calcula todas las métricas con el analista.
        4. Construye un reporte (dict).
        5. Invoca a cada exportador con el reporte.
        6. Devuelve el reporte para que el caller pueda inspeccionarlo.
        """
        transacciones_cop = [self.analista.convertir_a_cop(transaccion, self.tasas) for transaccion in self.parser.parse(source)]

        reporte: dict[str, object] = {}
        for metrica_name in dir(self.analista):
            metrica_func = getattr(self.analista, metrica_name)
            if not callable(metrica_func) or metrica_name.startswith('_') or metrica_name == 'convertir_a_cop':
                continue

            if metrica_name == 'total_aprobado_streaming':
                reporte[metrica_name] = metrica_func(self.parser, source, self.tasas)
                continue

            reporte[metrica_name] = metrica_func(transacciones_cop)

        for exportador in self.exportadores:
            exportador.exportar(reporte)
        return reporte