from dataclasses import dataclass
from decimal import Decimal, getcontext
from functools import total_ordering

getcontext().prec = 28

@total_ordering
@dataclass(frozen=True, slots=True)
class Dinero:
    monto: Decimal = Decimal(0)
    moneda: str = "COP"
    
    def __post_init__(self):
        if self.monto < 0: 
            raise ValueError("Monto no puede ser negativo")
        if len(self.moneda) != 3:
            raise ValueError("Moneda invalida")
        
    def _is_valid_cmp(self, other):
        return hasattr(other, "moneda") and hasattr(other, "monto")
        
    def __add__(self, other):
        if not self._is_valid_cmp(other): return NotImplemented
        if self.moneda != other.moneda: raise ValueError("Monedas diferentes")
        return Dinero(self.monto + other.monto, self.moneda)
    
    def __sub__(self, other):
        if not self._is_valid_cmp(other): return NotImplemented
        if self.moneda != other.moneda: raise ValueError("Monedas diferentes")
        if self.monto < other.monto: raise ValueError("Resultado no puede ser negativo")
        return Dinero(self.monto - other.monto, self.moneda)
        
    def __lt__(self, other):
        if not self._is_valid_cmp(other): return NotImplemented
        if self.moneda != other.moneda: raise ValueError("Monedas diferentes")
        return self.monto < other.monto
     
    def __eq__(self, other ):
        if not self._is_valid_cmp(other): return NotImplemented
        if self.moneda != other.moneda: raise ValueError("Monedas diferentes")
        return self.monto == other.monto
    
    def __str__(self):
        return f"{self.monto:,.2f} {self.moneda}"