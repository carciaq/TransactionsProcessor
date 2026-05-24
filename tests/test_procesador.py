from datetime import datetime
from decimal import Decimal
import json
from etl.analytics.analista import Analista
from etl.domain.dinero import Dinero
from etl.domain.transaccion import Transaccion
from etl.pipeline.procesador import ProcesadorTransacciones

from dataclasses import is_dataclass, asdict
from typing import Any


class ParserMock:
    def __init__(self, transacciones):
        self.transacciones = transacciones
        self.calls = 0

    def parse(self, source):
        self.calls += 1
        return list(self.transacciones)


class ExportadorFake:
    def __init__(self):
        self.reporte = None

    def exportar(self, reporte):
        self.reporte = reporte


def test_procesador_ejecuta_flujo_completo_sin_disco():
    transacciones = [
        Transaccion(
            id="a",
            fecha=datetime(2026, 5, 20, 8, 15, 30),
            comercio_id="com-1",
            comercio_nombre="tienda alfa",
            cliente_id="cli-1",
            ciudad="bogota",
            valor=Dinero(Decimal("10000"), "COP"),
            estado="aprobada",
            canal="web"
        ),
        Transaccion(
            id="b",
            fecha=datetime(2026, 5, 20, 8, 15, 30),
            comercio_id="com-1",
            comercio_nombre="tienda alfa",
            cliente_id="cli-1",
            ciudad="",
            valor=Dinero(Decimal("5"), "USD"),
            estado="aprobada",
            canal="web"
        ),
        Transaccion(
            id="c",
            fecha=datetime(2026, 5, 20, 8, 15, 30),
            comercio_id="com-2",
            comercio_nombre="la uvita",
            cliente_id="cli-1",
            ciudad="cali",
            valor=Dinero(Decimal("3000"), "COP"),
            estado="rechazada",
            canal="ventanilla"
        )
    ]
    parser = ParserMock(transacciones)
    exportador = ExportadorFake()
    procesador = ProcesadorTransacciones(
        parser=parser,
        analista=Analista(),
        exportadores=[exportador],
        tasas={"COP": 1.0, "USD": 4100.5},
    )

    reporte = procesador.procesar("ignored")
    print(transacciones)
    
    esperado = {
        "ids_aprobadas": ["a", "b"],
        "ciudades_unicas": {"bogota", "cali"},
        "comercio_por_id": {
            "com-1": "tienda alfa",
            "com-2": "la uvita"
        },
        "detectar_duplicados": set(),
        "clientes_frecuentes": set(),
        "montos_por_canal": {
            "web": Dinero(monto=Decimal('30502.5'), moneda='COP')
        },
        "top_n_comercios_por_monto": [('com-1', Dinero(monto=Decimal('30502.5'), moneda='COP'))],
        "total_aprobado_streaming": Dinero(monto=Decimal('30502.5'), moneda='COP')
    }
    
    

    assert parser.calls == 2
    assert exportador.reporte == reporte
    assert reporte == esperado
