# ETL de Transacciones

Proyecto ETL en Python para parsear transacciones, convertir montos a COP, calcular métricas y exportar reportes.

## 1) Instalación y ejecución

Notas:
- El repositorio usa layout `src/`.

### Instalar entorno (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install taskipy
python -m pip install pytest (si quieres correr tests)
```

### Correr tests

```powershell
cd src
python -m pytest -q
```

### Ejecutar ETL

```powershell
cd src
python -m etl --input ../data/transacciones.csv --tasas ../data/tasas.json --out ../data/reporte.json --modo ("silencioso","verboso")
```
o ejecutar shorcut:

```bash
cd src
task runp
```

## 2) Mapa de reglas pythónicas (archivo y línea)

Elementos obligatorios pedidos y su ubicación actual:

1. List comprehension real:
	- `src/etl/analytics/analista.py:12`
	- `return [t.id for t in txs if t.estado == "aprobada"]`

2. Dict comprehension real:
	- `src/etl/analytics/analista.py:18`
	- `return {t.comercio_id: t.comercio_nombre for t in txs if t.comercio_nombre != ''}`

3. Set comprehension real:
	- `src/etl/analytics/analista.py:15`
	- `return {t.ciudad for t in txs if t.ciudad != ''}`

4. Generator expression real:
	- `src/etl/analytics/analista.py:21`
	- `sum((self.convertir_a_cop(...) for t in parser.parse(source) ...), ...)`

5. Uso de `with` para abrir archivo de entrada:
	- `src/etl/parsers/csv_parser.py:14`
	- `with open(source) as data:`

6. Uso de `yield` en `ParserCSV.parse`:
	- `src/etl/parsers/csv_parser.py:19`
	- `yield Transaccion(...)`

7. Clase/función seleccionada condicionalmente en tiempo de ejecución:
	- `src/etl/__main__.py:31`
	- `if args.modo == 'verboso': Procesador.exportadores.append(ExportadorConsola())`
	- Aquí se decide condicionalmente agregar una clase exportadora al flujo.

## 3) Decisiones de diseño

### ¿Por qué `Dinero` es un Value Object?

`Dinero` representa un concepto de dominio sin identidad propia (dos montos iguales en misma moneda son equivalentes), con reglas internas claras (`monto >= 0`, moneda válida), y operaciones cerradas (`+`, `-`, comparaciones). Por eso se modela como objeto inmutable y comparable por valor.

### ¿Por qué `Parser` es ABC y `Exportador` es Protocol?

- `Parser` como ABC fuerza un contrato de herencia explícita con método abstracto `parse`, útil cuando la jerarquía está controlada por el proyecto.
- `Exportador` como `Protocol` habilita tipado estructural (duck typing): cualquier objeto con `exportar(reporte)` sirve, sin heredar de una base concreta. Esto simplifica fakes en pruebas y extensiones rápidas.

### ¿Por qué `Transaccion` es `frozen`?

Una transacción parseada representa un hecho histórico. Hacerla inmutable (`@dataclass(frozen=True)`) evita mutaciones accidentales durante el pipeline y facilita razonamiento, caching y tests deterministas.

### ¿Por qué streaming?

La lectura en streaming (`yield`) evita cargar todo el archivo al inicio, reduce memoria pico y permite procesar datasets grandes de forma incremental.

### Campos elegidos para `Transaccion` y por qué

- `id`: trazabilidad e identificación única.
- `fecha`: orden temporal y análisis por ventana de tiempo.
- `comercio_id`, `comercio_nombre`: agregaciones por comercio.
- `cliente_id`: análisis de frecuencia/recurrencia.
- `ciudad`: segmentación geográfica.
- `valor` (`Dinero`): monto + moneda con invariantes de dominio.
- `estado`: filtros de negocio (aprobada/rechazada).
- `canal`: análisis por canal de venta (web/app/pos/etc.).

## 4) Justificación de estructura por método de `Analista`

Referencia: `src/etl/analytics/analista.py`.

1. `ids_aprobadas`
	- Estructura: list comprehension.
	- Motivo: obtener secuencia ordenada de IDs filtrando por estado.

2. `ciudades_unicas`
	- Estructura: set comprehension.
	- Motivo: deduplicar ciudades en una sola pasada.

3. `comercio_por_id`
	- Estructura: dict comprehension.
	- Motivo: mapear clave-valor directo `id -> nombre` de forma declarativa.

4. `total_aprobado_streaming`
	- Estructura: generator expression dentro de `sum`.
	- Motivo: acumular en estilo streaming sin lista intermedia, ideal para memoria.

5. `detectar_duplicados`
	- Estructura: `Counter` + set comprehension.
	- Motivo: conteo eficiente de ocurrencias y extracción de IDs repetidos.

6. `top_n_comercios_por_monto`
	- Estructura: `defaultdict` para acumulación + `sorted(..., reverse=True)[:n]`.
	- Motivo: agregar montos por llave y luego ranking top-N.

7. `clientes_frecuentes`
	- Estructura: `Counter(...).items()` + set comprehension con umbral.
	- Motivo: filtrar clientes por frecuencia en forma compacta.

8. `montos_por_canal`
	- Estructura: `defaultdict` para acumulación por canal.
	- Motivo: sumar incrementalmente por clave sin condicionales de inicialización.

9. `convertir_a_cop`
	- Estructura: función de transformación pura (entrada `Transaccion`, salida `Transaccion`).
	- Motivo: separar la lógica de conversión de moneda del resto del pipeline y mantener inmutabilidad.

