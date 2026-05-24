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
import json

def main():
    parser = argparse.ArgumentParser(description='Procesar transacciones y generar un reporte.')
    parser.add_argument('--input', required=True, help='Archivo CSV de transacciones')
    parser.add_argument('--tasas', required=True, help='Archivo JSON con tasas de conversión')
    parser.add_argument('--out', required=True, help='Archivo de salida para el reporte')
    parser.add_argument('--modo', choices=['silencioso', 'verboso'], default='silencioso', help='Modo de ejecución')
    
    args = parser.parse_args()
    
    Procesador = ProcesadorTransacciones(
        parser=CSVParser(),
        analista=Analista(),
        exportadores=[ExportadorConsola(), ExportadorJSON(args.out)] if args.modo == 'verboso' else [ExportadorJSON(args.out)],
        tasas= json.load(open(args.tasas, 'r', encoding='utf-8')) 
    )
    
    Procesador.procesar(args.input)
    
if __name__ == "__main__":
    main()