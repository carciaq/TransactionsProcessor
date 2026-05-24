from decimal import Decimal
import pytest
from etl.domain.dinero import Dinero

def test_suma_de_dinero_en_misma_moneda():
    resultado = Dinero(Decimal("10.50"), "COP") + Dinero(Decimal("4.25"), "COP")

    assert resultado == Dinero(Decimal("14.75"), "COP")


def test_error_al_sumar_monedas_distintas():
    with pytest.raises(ValueError, match="Monedas diferentes"):
        _ = Dinero(Decimal("10"), "COP") + Dinero(Decimal("5"), "USD")


def test_error_al_crear_monto_negativo():
    with pytest.raises(ValueError, match="Monto no puede ser negativo"):
        Dinero(Decimal("-1"), "COP")


def test_comparacion_menor_y_mayor():
    menor = Dinero(Decimal("10"), "COP")
    mayor = Dinero(Decimal("20"), "COP")

    assert menor < mayor
    assert mayor > menor
