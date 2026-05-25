from collections.abc import Iterable
from collections import Counter, defaultdict
from decimal import Decimal
from etl.domain.transaccion import Transaccion
from etl.domain.dinero import Dinero
from etl.parsers.base import Parser
import logging


class Analista:
    
    def ids_aprobadas(self, txs: Iterable[Transaccion]) -> list[str]:
        try:
            return [t.id for t in txs if t.estado == "aprobada"]
        except Exception as e:
            logging.error(f"Error al calcular IDs aprobadas: {e}")
            return []

    def ciudades_unicas(self, txs: Iterable[Transaccion]) -> set[str]:
        try:
            return {t.ciudad for t in txs if t.ciudad != ''} #Se supone que lo limpio en el parser??
        except Exception as e:
            logging.error(f"Error al calcular ciudades únicas: {e}")
            return set()

    def comercio_por_id(self, txs: Iterable[Transaccion]) -> dict[str, str]:
        try:
            return {t.comercio_id: t.comercio_nombre for t in txs if t.comercio_nombre != ''}
        except Exception as e:
            logging.error(f"Error al calcular comercios por ID: {e}")
            return {}

    def total_aprobado_streaming(self, parser: Parser, source: str, tasas: dict[str, float]) -> Dinero:
        try:
            total = Dinero(monto=0, moneda="COP")
            for t in parser.parse(source):
                if t.estado == "aprobada":
                    transaccion_cop = self.convertir_a_cop(t, tasas)
                    if transaccion_cop is not None:
                        total += transaccion_cop.valor
            return total
        except Exception as e:
            logging.error(f"Error al calcular el total aprobado: {e}")
            return None

    def detectar_duplicados(self, txs: Iterable[Transaccion]) -> set[str]:
        try:
            return {i for i in Counter(t.id for t in txs).elements() if Counter(t.id for t in txs)[i] > 1}
        except Exception as e:
            logging.error(f"Error al detectar duplicados: {e}")
            return set()

    def top_n_comercios_por_monto(self, txs: Iterable[Transaccion], n: int = 10) -> list[tuple[str, Dinero]]:
        try:
            montos_por_comercio = defaultdict(Dinero)
            for t in txs:
                if t.estado == "aprobada" : montos_por_comercio[t.comercio_id] += t.valor 
            return sorted(montos_por_comercio.items(), key=lambda x: x[1], reverse=True)[:n]
        except Exception as e:
            logging.error(f"Error al calcular top comercios por monto: {e}")
            return []

    def clientes_frecuentes(self, txs: Iterable[Transaccion], umbral: int = 5) -> set[str]:
        try:
            return {i[0] for i in Counter(t.cliente_id for t in txs).items() if i[1] > umbral}
        except Exception as e:
            logging.error(f"Error al calcular clientes frecuentes: {e}")
            return set()

    def montos_por_canal(self, txs: Iterable[Transaccion]) -> dict[str, Dinero]:
        try:
            canales: dict[str, Dinero] = defaultdict(lambda: Dinero(monto=Decimal(0), moneda="COP"))
            for t in txs:
                if t.estado == "aprobada":canales[t.canal] = canales[t.canal] + t.valor
            return canales
        except Exception as e:
            logging.error(f"Error al calcular montos por canal: {e}")
            return {}
    
    def convertir_a_cop(self, tx: Transaccion, tasas: dict[str, float]) -> Transaccion:
        try:
            tasa = tasas.get(tx.valor.moneda)
            if tasa : tasa = Decimal(str(tasa)) 
            else: raise ValueError(f"No se encontró una tasa de conversión para la moneda {tx.valor.moneda}")
            conversion = tx.valor.monto * tasa
            return Transaccion(
                id=tx.id,
                fecha=tx.fecha,
                comercio_id=tx.comercio_id,
                comercio_nombre=tx.comercio_nombre,
                cliente_id=tx.cliente_id,
                ciudad=tx.ciudad,
                valor=Dinero(monto=conversion, moneda="COP"),
                estado=tx.estado,
                canal=tx.canal
            )
        except Exception as e:
            logging.error(f"Error al convertir la transacción {tx.id}: {e}")
            return None
