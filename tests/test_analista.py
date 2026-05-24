from datetime import datetime
from decimal import Decimal
from etl.analytics.analista import Analista
from etl.domain.dinero import Dinero
from etl.domain.transaccion import Transaccion


class ParserFake:
    def __init__(self, transacciones):
        self._transacciones = transacciones

    def parse(self, source):
        return list(self._transacciones)


def transaccion(**overrides):
    base = {
        "id": "tx-1",
        "fecha": datetime(2026, 5, 20, 8, 15, 30),
        "comercio_id": "com-1",
        "comercio_nombre": "tienda alfa",
        "cliente_id": "cli-1",
        "ciudad": "bogota",
        "valor": Dinero(Decimal("10"), "COP"),
        "estado": "aprobada",
        "canal": "web",
    }
    base.update(overrides)
    return Transaccion(**base)


def test_ids_aprobadas():
    analista = Analista()
    txs = [transaccion(id="a"), transaccion(id="b", estado="rechazada"), transaccion(id="c")]

    assert analista.ids_aprobadas(txs) == ["a", "c"]


def test_ciudades_unicas():
    analista = Analista()
    txs = [transaccion(ciudad="bogota"), transaccion(ciudad="medellin"), transaccion(ciudad="bogota"), transaccion(ciudad="")]

    assert analista.ciudades_unicas(txs) == {"bogota", "medellin"}


def test_comercio_por_id():
    analista = Analista()
    txs = [transaccion(comercio_id="com-1", comercio_nombre="alpha"), transaccion(comercio_id="com-2", comercio_nombre="beta")]

    assert analista.comercio_por_id(txs) == {"com-1": "alpha", "com-2": "beta"}


def test_total_aprobado_streaming():
    analista = Analista()
    txs = [
        transaccion(valor=Dinero(Decimal("10"), "COP")),
        transaccion(id="b", valor=Dinero(Decimal("2"), "USD")),
        transaccion(id="c", estado="rechazada", valor=Dinero(Decimal("100"), "COP")),
    ]
    parser = ParserFake(txs)

    assert analista.total_aprobado_streaming(parser, "ignored", {"COP": 1.0, "USD": 4100.5}) == Dinero(Decimal("8211.0"), "COP")


def test_detectar_duplicados():
    analista = Analista()
    txs = [transaccion(id="dup"), transaccion(id="dup"), transaccion(id="uniq")]

    assert analista.detectar_duplicados(txs) == {"dup"}


def test_top_n_comercios_por_monto():
    analista = Analista()
    txs = [
        transaccion(comercio_id="c1", valor=Dinero(Decimal("10"), "COP")),
        transaccion(comercio_id="c2", valor=Dinero(Decimal("30"), "COP")),
        transaccion(comercio_id="c1", valor=Dinero(Decimal("5"), "COP")),
        transaccion(comercio_id="c3", valor=Dinero(Decimal("1"), "COP")),
    ]

    assert analista.top_n_comercios_por_monto(txs, n=2) == [("c2", Dinero(Decimal("30"), "COP")), ("c1", Dinero(Decimal("15"), "COP"))]


def test_clientes_frecuentes():
    analista = Analista()
    txs = [
        transaccion(cliente_id="cli-1"),
        transaccion(cliente_id="cli-1"),
        transaccion(cliente_id="cli-1"),
        transaccion(cliente_id="cli-2"),
        transaccion(cliente_id="cli-2"),
    ]

    assert analista.clientes_frecuentes(txs, umbral=2) == {"cli-1"}


def test_montos_por_canal():
    analista = Analista()
    txs = [
        transaccion(canal="web", valor=Dinero(Decimal("10"), "COP")),
        transaccion(canal="web", valor=Dinero(Decimal("5"), "COP")),
        transaccion(canal="app", valor=Dinero(Decimal("7"), "COP")),
    ]

    assert analista.montos_por_canal(txs) == {
        "web": Dinero(Decimal("15"), "COP"),
        "app": Dinero(Decimal("7"), "COP"),
    }


def test_convertir_a_cop():
    analista = Analista()
    tx = transaccion(valor=Dinero(Decimal("2"), "USD"))

    convertido = analista.convertir_a_cop(tx, {"USD": 4100.5})

    assert convertido.valor == Dinero(Decimal("8201.0"), "COP")
    assert convertido.id == tx.id
    assert convertido.comercio_id == tx.comercio_id
    assert convertido.estado == tx.estado
