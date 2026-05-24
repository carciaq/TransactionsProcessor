from abc import ABC, abstractmethod
from collections.abc import Iterator
from etl.domain.transaccion import Transaccion

class Parser(ABC):
    
    @abstractmethod
    def parse(self, source : str) -> Iterator[Transaccion]:
        #Lee una fuente y produce transacciones, una por una
        pass