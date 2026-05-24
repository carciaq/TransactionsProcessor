from decimal import Decimal
from etl.parsers.csv_parser import CSVParser
from etl.domain.dinero import Dinero


def test_csv_parser_salta_filas_malas_y_devuelve_las_buenas(tmp_path, caplog):
    csv_content = """id,fecha,comercio_id,comercio_nombre,cliente_id,ciudad,monto,moneda,estado,canal
ok-1,2026-05-20 08:15:30,com-1,tienda alfa,cli-1,bogota,120000,COP,aprobada,web
bad-1,2026-05-20 09:00:00,com-2,tienda beta,cli-2,medellin,abc,USD,aprobada,app
ok-2,2026-05-20 10:30:00,com-3,tienda gamma,cli-3,cali,42.50,EUR,rechazada,pos
bad-2,2026-99-99 10:30:00,com-4,tienda delta,cli-4,barranquilla,10,COP,aprobada,web
"""
    archivo = tmp_path / "transacciones.csv"
    archivo.write_text(csv_content, encoding="utf-8")

    parser = CSVParser()
    with caplog.at_level("WARNING"):
        transacciones = list(parser.parse(str(archivo)))

    assert [t.id for t in transacciones] == ["ok-1", "ok-2"]
    assert transacciones[0].valor == Dinero(Decimal("120000"), "COP")
    assert transacciones[1].valor == Dinero(Decimal("42.50"), "EUR")
    assert any("Error al parsear la fila 2" in record.message for record in caplog.records)
    assert any("Error al parsear la fila 4" in record.message for record in caplog.records)
