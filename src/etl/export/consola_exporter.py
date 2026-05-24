class ExportadorConsola:
    def exportar(self, reporte: dict) -> None:
        for clave, valor in reporte.items():
            print(f"{clave} = {valor}")