from collections.abc import Iterable
from collections import Counter, defaultdict
from decimal import Decimal
from etl.domain.transaccion import Transaccion
from etl.domain.dinero import Dinero
from etl.parsers.base import Parser


class Analista:
    
    def ids_aprobadas(self, txs: Iterable[Transaccion]) -> list[str]:
        return [t.id for t in txs if t.estado == "aprobada"]
    
    def ciudades_unicas(self, txs: Iterable[Transaccion]) -> set[str]:
        return {t.ciudad for t in txs if t.ciudad != ''} #Se supone que lo limpio en el parser??
    
    def comercio_por_id(self, txs: Iterable[Transaccion]) -> dict[str, str]:
        return {t.comercio_id: t.comercio_nombre for t in txs if t.comercio_nombre != ''}
    
    def total_aprobado_streaming(self, parser: Parser, source: str, tasas: dict[str, float]) -> Dinero:
        return sum((self.convertir_a_cop(t,tasas).valor for t in parser.parse(source) if t.estado == "aprobada"), Dinero(monto=0, moneda="COP"))
        
    
    def detectar_duplicados(self, txs: Iterable[Transaccion]) -> set[str]:
        return {i for i in Counter(t.id for t in txs).elements() if Counter(t.id for t in txs)[i] > 1}
    
    def top_n_comercios_por_monto(self, txs: Iterable[Transaccion], n: int = 10) -> list[tuple[str, Dinero]]:
        montos_por_comercio = defaultdict(Dinero)
        for t in txs:
            if t.estado == "aprobada" : montos_por_comercio[t.comercio_id] += t.valor 
        return sorted(montos_por_comercio.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def clientes_frecuentes(self, txs: Iterable[Transaccion], umbral: int = 5) -> set[str]:
        return {i[0] for i in Counter(t.cliente_id for t in txs).items() if i[1] > umbral}
    
    def montos_por_canal(self, txs: Iterable[Transaccion]) -> dict[str, Dinero]:
        canales: dict[str, Dinero] = defaultdict(lambda: Dinero(monto=Decimal(0), moneda="COP"))
        for t in txs:
            if t.estado == "aprobada":canales[t.canal] = canales[t.canal] + t.valor
        return canales
    
    def convertir_a_cop(self, tx: Transaccion, tasas: dict[str, float]) -> Transaccion:
        moneda_actual = tx.valor.moneda
        tasa = Decimal(str(tasas.get(moneda_actual, 1)))
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
