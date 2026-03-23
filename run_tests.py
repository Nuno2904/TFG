#!/usr/bin/env python3
"""
Script para ejecutar todos los tests y mostrar resultados en tiempo real
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Ejecuta todos los tests con pytest en modo verbose"""
    
    print("=" * 80)
    print("🧪 INICIANDO EJECUCIÓN DE TESTS")
    print("=" * 80)
    print()
    
    # Get the project root
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    print(f"📁 Directorio de tests: {tests_dir}")
    print(f"📁 Directorio raíz: {project_root}")
    print()
    
    # Preparar comando pytest
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir),
        "-v",                    # Verbose
        "--tb=short",            # Traceback corto
        "--color=yes",           # Con colores
        "-ra",                   # Resumen de todos los tests
    ]
    
    print(f"🔧 Ejecutando: {' '.join(cmd)}")
    print("=" * 80)
    print()
    
    # Ejecutar pytest
    result = subprocess.run(cmd, cwd=project_root)
    
    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print(f"❌ ALGUNOS TESTS FALLARON (exit code: {result.returncode})")
    print("=" * 80)
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
