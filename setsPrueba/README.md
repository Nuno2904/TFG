# 📊 Conjunto de Prueba de Datasets

Carpeta con archivos de prueba para validar que el sistema de carga de archivos:
- ✅ Acepta solo formatos válidos (CSV/XLSX)
- ✅ Rechaza extensiones inválidas
- ✅ Valida automáticamente columnas de fecha y numéricas
- ✅ Detecta datos faltantes
- ✅ Rechaza archivos sin datos numéricos válidos

## 🚀 Generación de Archivos XLSX

### Opción 1: Usar el script Python (RECOMENDADO)

```bash
# Ir a la carpeta setsPrueba
cd TFG/setsPrueba

# Asegurarse de tener las dependencias
pip install openpyxl pandas

# Ejecutar el script
python crear_xlsx.py
```

Esto generará automáticamente 8 archivos XLSX (válidos e inválidos).

### Opción 2: Crear manualmente en Excel

También puedes crear archivos `.xlsx` directamente en Excel con los mismos esquemas que los archivos CSV correspondientes.

## 📁 Archivos de Prueba

### ✅ VÁLIDOS (Deben aceptarse)

#### 01_VALIDO_datos_normales.csv
- **Descripción**: Dataset estándar con formato correcto
- **Columnas**: `date` (YYYY-MM-DD), `value` (numéricos)
- **Filas**: 20 datos
- **Resultado esperado**: ✅ ACEPTADO
- **Propósito**: Validar carga básica de datos normales

#### 08_VALIDO_fechas_DD-MM-YYYY.csv
- **Descripción**: Dataset con fechas en formato DD-MM-YYYY
- **Columnas**: `fecha` (DD-MM-YYYY), `precio` (numéricos)
- **Filas**: 50 datos
- **Resultado esperado**: ✅ ACEPTADO
- **Propósito**: Verificar que el auto-detector reconoce fechas en diferentes formatos

#### 09_VALIDO_nombres_columnas_diferentes.csv
- **Descripción**: Dataset con nombres de columnas no estándar
- **Columnas**: `timestamp` (fecha), `data_value` (numéricos)
- **Filas**: 20 datos
- **Resultado esperado**: ✅ ACEPTADO
- **Propósito**: Probar auto-detección de columnas con nombres genéricos

#### 10_VALIDO_con_negativos.csv
- **Descripción**: Dataset con valores numéricos negativos
- **Columnas**: `date`, `value` (incluyendo negativos)
- **Filas**: 20 datos
- **Resultado esperado**: ✅ ACEPTADO
- **Propósito**: Verificar que se aceptan números negativos

---

### ❌ INVÁLIDOS (Deben rechazarse)

#### 02_INVALIDO_tres_columnas.csv
- **Descripción**: Dataset con 3 columnas en lugar de 2
- **Columnas**: `date`, `value`, `extra_column`
- **Razón de rechazo**: Sistema espera 2 columnas (fecha + numérica)
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Validar que no acepta datos con columnas extras

#### 03_INVALIDO_datos_faltantes.csv
- **Descripción**: Dataset con valores faltantes en la columna numérica
- **Problema**: Celdas vacías en algunos registros
- **Razón de rechazo**: Validación falla por < 50% de datos válidos
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Verificar validación de completitud de datos

#### 04_INVALIDO_valores_texto.csv
- **Descripción**: Dataset con texto en lugar de números
- **Columnas**: `date`, `value` (con valores como "alto", "bajo", "muy_alto")
- **Razón de rechazo**: La columna de valores no es numérica
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Verificar que rechaza valores no numéricos

#### 05_INVALIDO_solo_una_columna.csv
- **Descripción**: Dataset con una sola columna
- **Columnas**: Solo `value`
- **Razón de rechazo**: No encuentra columna de fecha
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Validar que requiere fecha + valor

#### 06_INVALIDO_fechas_invalidas.csv
- **Descripción**: Dataset con fechas claramente inválidas
- **Problemas**: Texto aleatorio, formatos imposibles, fechas que no existen
- **Razón de rechazo**: < 50% de fechas válidas en auto-detección
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Verificar validación de formato de fechas

#### 07_INVALIDO_archivo_vacio.csv
- **Descripción**: Archivo con solo encabezados, sin datos
- **Contenido**: Solo `date,value` (sin filas de datos)
- **Razón de rechazo**: Sin datos para procesar
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Validar que rechaza archivos vacíos

#### 11_INVALIDO_todas_fechas_iguales.csv
- **Descripción**: Dataset donde todas las fechas son idénticas
- **Problema**: No hay variabilidad temporal (todas son 2023-01-01)
- **Razón de rechazo**: Serie temporal sin progresión temporal real
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Verificar que detecta series sin variación temporal

#### 12_INVALIDO_extension_txt.txt
- **Descripción**: Archivo con contenido CSV pero extensión incorrecta
- **Extensión**: `.txt` en lugar de `.csv`
- **Razón de rechazo**: Solo se aceptan .csv y .xlsx
- **Resultado esperado**: ❌ RECHAZADO
- **Propósito**: Validar que rechaza tipos de archivo no permitidos

---

## 🧪 Cómo Probar

### En la interfaz web:
1. Ve a la sección **📁 Mis Archivos**
2. Haz clic en **"Subir Dataset"**
3. Intenta subir cada archivo en orden
4. Verifica que:
   - ✅ Los archivos VÁLIDOS se acepten
   - ❌ Los archivos INVÁLIDOS muestren mensajes de error específicos

### Validaciones esperadas:
```
Archivo válido → "Dataset cargado exitosamente"
Extensión inválida → "Formato de archivo no permitido (solo CSV/XLSX)"
Datos incompletos → "Datos insuficientes o inválidos"
Sin columna numérica → "No se encontró columna numérica válida"
Sin columna de fecha → "No se encontró columna de fecha válida"
Archivo vacío → "El archivo no contiene datos válidos"
```

---

## � Resumen de Archivos

| # | Archivo | Tipo | Estado | Razón |
|---|---------|------|--------|-------|
| 1 | 01_VALIDO_datos_normales.csv | CSV | ✅ V | Formato estándar correcto |
| 2 | 02_INVALIDO_tres_columnas.csv | CSV | ❌ I | Tiene 3 columnas (2 esperadas) |
| 3 | 03_INVALIDO_datos_faltantes.csv | CSV | ❌ I | Muchos valores vacíos |
| 4 | 04_INVALIDO_valores_texto.csv | CSV | ❌ I | Valores no numéricos |
| 5 | 05_INVALIDO_solo_una_columna.csv | CSV | ❌ I | Sin columna de fecha |
| 6 | 06_INVALIDO_fechas_invalidas.csv | CSV | ❌ I | Fechas mal formateadas |
| 7 | 07_INVALIDO_archivo_vacio.csv | CSV | ❌ I | Solo encabezados |
| 8 | 08_VALIDO_fechas_DD-MM-YYYY.csv | CSV | ✅ V | Detecta fechas DD-MM-YYYY |
| 9 | 09_VALIDO_nombres_columnas_diferentes.csv | CSV | ✅ V | Auto-detecta columnas genéricas |
| 10 | 10_VALIDO_con_negativos.csv | CSV | ✅ V | Acepta números negativos |
| 11 | 11_INVALIDO_todas_fechas_iguales.csv | CSV | ❌ I | Sin variación temporal |
| 12 | 12_INVALIDO_extension_txt.txt | TXT | ❌ I | Extensión no permitida |
| 13 | 13_INVALIDO_extension_json.json | JSON | ❌ I | Extensión no permitida |
| 14 | 14_INVALIDO_extension_xml.xml | XML | ❌ I | Extensión no permitida |
| 15 | 15_INVALIDO_extension_tsv.tsv | TSV | ❌ I | Extensión no permitida |
| 16 | 16_INVALIDO_extension_doc.doc | DOC | ❌ I | Extensión no permitida |
| 17 | 17_INVALIDO_extension_docx.docx | DOCX | ❌ I | Extensión no permitida |
| 18 | 18_INVALIDO_extension_pdf.pdf | PDF | ❌ I | Extensión no permitida |
| 19* | 19_VALIDO_datos_normales.xlsx | XLSX | ✅ V | Generado por script |
| 20* | 20_VALIDO_mucho_datos.xlsx | XLSX | ✅ V | Generado por script (100 filas) |
| 21* | 21_INVALIDO_sin_columna_fecha.xlsx | XLSX | ❌ I | Generado por script |
| 22* | 22_INVALIDO_valores_texto.xlsx | XLSX | ❌ I | Generado por script |
| 23* | 23_INVALIDO_datos_faltantes.xlsx | XLSX | ❌ I | Generado por script |
| 24* | 24_INVALIDO_tres_columnas.xlsx | XLSX | ❌ I | Generado por script |
| 25* | 25_VALIDO_con_negativos.xlsx | XLSX | ✅ V | Generado por script |
| 26* | 26_INVALIDO_vacio.xlsx | XLSX | ❌ I | Generado por script |

**Nota**: Los archivos marcados con * necesitan ser generados ejecutando `python crear_xlsx.py`

---

## �📈 Parámetros de Validación del Sistema

| Parámetro | Valor |
|-----------|-------|
| Formatos permitidos | CSV, XLSX |
| Tamaño máximo | 5 MB |
| Columnas requeridas | 2 (Fecha + Numérico) |
| Validez de fecha mínima | ≥ 50% de la columna |
| Datos numéricos mínimos | ≥ 50% de la columna |
| Puntos mínimos recomendados | 20+ registros |

---

## 📝 Notas

- Los archivos válidos pueden usarse para entrenar modelos Prophet, ARIMA y SARIMA
- El sistema detecta automáticamente fechas en múltiples formatos (DD-MM-YYYY, YYYY-MM-DD, etc.)
- El sistema busca automáticamente columnas de fecha y numéricas, no requiere nombres específicos
- Los valores nulos/vacíos se consideran como dados faltantes
