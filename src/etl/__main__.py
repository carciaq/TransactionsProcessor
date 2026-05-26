"""Procesar cli y ejecutar el proceso ETL:
python -m etl --input transacciones.csv \
--tasas tasas.json \
--out reporte.json \
--modo silencioso"""

import argparse
from etl.pipeline.procesador import ProcesadorTransacciones
from etl.parsers.csv_parser import CSVParser
from etl.analytics.analista import Analista
from etl.export.consola_exporter import ExportadorConsola
from etl.export.json_exporter import ExportadorJSON
from etl.exceptions.exceptions import CSVError, RowError, FormatError, DuplicateIDError
from etl.exceptions.logger import logger
import json
import glob


def iter_csv_errors(cls):
    for subclass in cls.__subclasses__():
        yield subclass

input_files = glob.glob('../data/*.csv')
input_files.append('../data/corrupto.csv') 

def main():
    parser = argparse.ArgumentParser(description='Procesar transacciones y generar un reporte.')
    parser.add_argument('--tasas', required=True, help='Archivo JSON con tasas de conversión')
    parser.add_argument('--out', required=True, help='Archivo de salida para el reporte')
    parser.add_argument('--modo', choices=['silencioso', 'verboso'], default='silencioso', help='Modo de ejecución')
    
    args = parser.parse_args()

    logger.info(f"Archivos a procesar: {input_files}")
    
    failed = 0
    total_procesadas = 0
    for i, f in enumerate(input_files):
        logger.info(f"Procesando: {f}")
        try:
            
            Procesador = ProcesadorTransacciones(
                parser=CSVParser(),
                analista=Analista(),
                exportadores=[ExportadorJSON(args.out)],
                tasas= json.load(open(args.tasas, 'r', encoding='utf-8')) 
            )
            if args.modo == 'verboso': Procesador.exportadores.append(ExportadorConsola())
            Procesador.procesar(f)
            total_procesadas += Procesador.procesadas
            logger.info(f"Archivo {f} procesado exitosamente. Total filas procesadas: {Procesador.procesadas}")
        except FileNotFoundError as e:
            failed += 1
            logger.error(e)
    
    logger.info(f"""
=================== Reporte Final ===================
Total archivos procesados: {len(input_files)-failed}/{len(input_files)}
Filas Procesadas {total_procesadas}
Filas con errores: {sum(subclass.calls for subclass in iter_csv_errors(CSVError))}
Tasa de exito: {100 * (total_procesadas) / (total_procesadas + sum(subclass.calls for subclass in iter_csv_errors(CSVError))):.2f}%

Errores por tipo:
{chr(10).join(f'{error_type.__name__}: {error_type.calls}' for error_type in iter_csv_errors(CSVError))}
"""
)
    
if __name__ == "__main__":
    main()