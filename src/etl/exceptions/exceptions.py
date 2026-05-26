
class CSVError(Exception):
    """Excepción base para errores relacionados con CSV."""
    calls = 0

    @classmethod
    def increment_calls(cls) -> None:
        cls.calls += 1

    pass

class RowError(CSVError):
    """Excepción para errores específicos de una fila en el CSV."""
    def __init__(self, row_number: int, row_data: dict, source: str, original_exception: Exception):
        type(self).increment_calls()
        self.row_number = row_number
        self.row_data = row_data
        self.source = source
        self.original_exception = original_exception
        super().__init__(f"Fila {row_number} del archivo {source} saltada \n data: {row_data} \n - {original_exception}")

class DuplicateIDError(CSVError):
    """Excepción para detectar IDs duplicados en el CSV."""
    def __init__(self, row_number: int, row_data: dict, source: str):
        type(self).increment_calls()
        self.row_number = row_number
        self.row_data = row_data
        self.source = source
        super().__init__(f"ID duplicado encontrado en la fila {row_number} del archivo {source} \n data: {row_data} \n")
        
class FormatError(CSVError):
    """Excepción para errores de formato en el CSV."""
    def __init__(self, row_number: int, row_data: dict, source: str, original_exception: Exception):
        type(self).increment_calls()
        self.row_number = row_number
        self.row_data = row_data
        self.source = source
        self.original_exception = original_exception
        super().__init__(f"Fila {row_number} del archivo {source} saltada \n data: {row_data} \n - {original_exception}")