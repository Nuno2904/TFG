#!/usr/bin/env python3
"""
🧪 Script para generar archivos XLSX para pruebas

Genera archivos Excel válidos e inválidos para probar la validación
del sistema de carga de datasets.

Requisito: pip install openpyxl pandas
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

try:
    import pandas as pd
    from openpyxl import Workbook
except ImportError:
    print("❌ Falta instalar las dependencias:")
    print("   pip install openpyxl pandas")
    sys.exit(1)

# Obtener la ruta de la carpeta de este script
script_dir = Path(__file__).parent
output_dir = script_dir

def crear_xlsx_valido_simple():
    """Crear archivo XLSX válido con 2 columnas normales"""
    print("📊 Creando: 19_VALIDO_datos_normales.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(20)]
    data = {
        'date': dates,
        'value': [100.5 + i*1.5 for i in range(20)]
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "19_VALIDO_datos_normales.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ✅ Creado: {output_file.name}")


def crear_xlsx_valido_mucho_datos():
    """Crear archivo XLSX válido con muchos datos (100 filas)"""
    print("📊 Creando: 20_VALIDO_mucho_datos.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    data = {
        'timestamp': dates,
        'price': [100.5 + i*0.8 for i in range(100)]
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "20_VALIDO_mucho_datos.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ✅ Creado: {output_file.name}")


def crear_xlsx_invalido_sin_fecha():
    """Crear XLSX inválido: sin columna de fecha"""
    print("📊 Creando: 21_INVALIDO_sin_columna_fecha.xlsx")
    
    data = {
        'value': [100.5 + i*1.5 for i in range(10)]
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "21_INVALIDO_sin_columna_fecha.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ❌ Creado: {output_file.name}")


def crear_xlsx_invalido_sin_numeros():
    """Crear XLSX inválido: columna numérica con texto"""
    print("📊 Creando: 22_INVALIDO_valores_texto.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
    data = {
        'date': dates,
        'status': ['alto', 'bajo', 'medio', 'alto', 'muy alto', 'bajo', 'medio', 'alto', 'bajo', 'muy bajo']
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "22_INVALIDO_valores_texto.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ❌ Creado: {output_file.name}")


def crear_xlsx_invalido_datos_faltantes():
    """Crear XLSX inválido: muchos datos faltantes"""
    print("📊 Creando: 23_INVALIDO_datos_faltantes.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
    values = [100.5, None, None, 103.2, None, None, 106.2, None, None, 108.5]
    data = {
        'date': dates,
        'value': values
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "23_INVALIDO_datos_faltantes.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ❌ Creado: {output_file.name}")


def crear_xlsx_invalido_tres_columnas():
    """Crear XLSX inválido: 3 columnas"""
    print("📊 Creando: 24_INVALIDO_tres_columnas.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
    data = {
        'date': dates,
        'value': [100.5 + i*1.5 for i in range(10)],
        'extra_info': ['meta1', 'meta2', 'meta3', 'meta4', 'meta5', 'meta6', 'meta7', 'meta8', 'meta9', 'meta10']
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "24_INVALIDO_tres_columnas.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ❌ Creado: {output_file.name}")


def crear_xlsx_valido_negativos():
    """Crear XLSX válido con valores negativos"""
    print("📊 Creando: 25_VALIDO_con_negativos.xlsx")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(20)]
    values = [100.5 if i % 2 == 0 else -100.5 + i*2 for i in range(20)]
    data = {
        'date': dates,
        'value': values
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "25_VALIDO_con_negativos.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ✅ Creado: {output_file.name}")


def crear_xlsx_invalido_vacio():
    """Crear XLSX inválido: solo encabezados"""
    print("📊 Creando: 26_INVALIDO_vacio.xlsx")
    
    data = {
        'date': [],
        'value': []
    }
    df = pd.DataFrame(data)
    
    output_file = output_dir / "26_INVALIDO_vacio.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Datos")
    print(f"   ❌ Creado: {output_file.name}")


def main():
    print("\n" + "="*60)
    print("🧪 Generador de Archivos XLSX para Pruebas")
    print("="*60 + "\n")
    
    try:
        crear_xlsx_valido_simple()
        crear_xlsx_valido_mucho_datos()
        crear_xlsx_invalido_sin_fecha()
        crear_xlsx_invalido_sin_numeros()
        crear_xlsx_invalido_datos_faltantes()
        crear_xlsx_invalido_tres_columnas()
        crear_xlsx_valido_negativos()
        crear_xlsx_invalido_vacio()
        
        print("\n" + "="*60)
        print("✅ ¡Todos los archivos XLSX se crearon correctamente!")
        print("="*60)
        print(f"\n📁 Ubicación: {output_dir}\n")
        
    except Exception as e:
        print(f"\n❌ Error al crear archivos: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
