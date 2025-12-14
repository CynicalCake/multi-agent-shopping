"""
Script de verificación del sistema
Valida que todos los componentes estén correctamente instalados
"""

import sys
import os
from pathlib import Path

def verificar_estructura_archivos():
    """Verifica que todos los archivos necesarios existan."""
    print("="*80)
    print("1. VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("="*80)
    
    archivos_requeridos = [
        "server/app.py",
        "server/requirements.txt",
        "server/models/agente_recomendador.py",
        "server/utils/algoritmos_busqueda.py",
        "server/data/inventario/SUC001.json",
        "server/data/inventario/SUC002.json",
        "test_agente_recomendador.py",
        "ejemplos_api.py",
        "README.md",
        "SETUP.md"
    ]
    
    proyecto_root = Path(__file__).parent
    faltantes = []
    
    for archivo in archivos_requeridos:
        ruta = proyecto_root / archivo
        if ruta.exists():
            print(f"  ✓ {archivo}")
        else:
            print(f"  ✗ {archivo} - NO ENCONTRADO")
            faltantes.append(archivo)
    
    if faltantes:
        print(f"\n  ⚠️  Faltan {len(faltantes)} archivo(s)")
        return False
    else:
        print(f"\n  ✓ Todos los archivos necesarios están presentes")
        return True


def verificar_dependencias():
    """Verifica que las dependencias de Python estén instaladas."""
    print("\n" + "="*80)
    print("2. VERIFICANDO DEPENDENCIAS DE PYTHON")
    print("="*80)
    
    dependencias = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("flask_socketio", "Flask-SocketIO"),
        ("socketio", "python-socketio"),
        ("engineio", "python-engineio")
    ]
    
    faltantes = []
    
    for modulo, nombre in dependencias:
        try:
            __import__(modulo)
            print(f"  ✓ {nombre}")
        except ImportError:
            print(f"  ✗ {nombre} - NO INSTALADO")
            faltantes.append(nombre)
    
    if faltantes:
        print(f"\n  ⚠️  Faltan {len(faltantes)} dependencia(s)")
        print(f"  Instalar con: pip install -r server/requirements.txt")
        return False
    else:
        print(f"\n  ✓ Todas las dependencias están instaladas")
        return True


def verificar_inventarios():
    """Verifica que los inventarios sean válidos."""
    print("\n" + "="*80)
    print("3. VERIFICANDO INVENTARIOS")
    print("="*80)
    
    import json
    
    proyecto_root = Path(__file__).parent
    inventarios = ["SUC001", "SUC002"]
    
    for sucursal_id in inventarios:
        ruta = proyecto_root / "server" / "data" / "inventario" / f"{sucursal_id}.json"
        
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            nombre = data.get('nombre', 'Sin nombre')
            productos = data.get('productos', [])
            
            print(f"\n  ✓ {sucursal_id} - {nombre}")
            print(f"    Productos: {len(productos)}")
            
            if productos:
                categorias = set(p.get('categoria', 'sin_categoria') for p in productos)
                print(f"    Categorías: {len(categorias)}")
                
                # Verificar estructura de productos
                producto_ejemplo = productos[0]
                campos_requeridos = ['id', 'nombre', 'precio', 'categoria', 'importancia', 'cantidad_tipica']
                campos_ok = all(campo in producto_ejemplo for campo in campos_requeridos)
                
                if campos_ok:
                    print(f"    Estructura: ✓ Válida")
                else:
                    print(f"    Estructura: ✗ Falta algún campo")
            
        except Exception as e:
            print(f"  ✗ {sucursal_id} - ERROR: {e}")
            return False
    
    print(f"\n  ✓ Todos los inventarios son válidos")
    return True


def verificar_importacion_agente():
    """Verifica que el agente recomendador se pueda importar."""
    print("\n" + "="*80)
    print("4. VERIFICANDO IMPORTACIÓN DEL AGENTE")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
        from server.models.agente_recomendador import AgenteRecomendador
        print(f"  ✓ AgenteRecomendador importado correctamente")
        
        # Intentar crear una instancia
        agente = AgenteRecomendador('SUC001')
        print(f"  ✓ Instancia creada: {agente.nombre_sucursal}")
        print(f"  ✓ Productos cargados: {len(agente.productos)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error al importar agente: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_algoritmo():
    """Verifica que el algoritmo de Temple Simulado funcione."""
    print("\n" + "="*80)
    print("5. VERIFICANDO ALGORITMO DE TEMPLE SIMULADO")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
        from server.utils.algoritmos_busqueda import TempleSimulado
        
        print(f"  ✓ TempleSimulado importado correctamente")
        
        # Crear instancia y probar optimización simple
        ts = TempleSimulado()
        print(f"  ✓ Instancia creada")
        print(f"    Temperatura inicial: {ts.temperatura_inicial}")
        print(f"    Temperatura mínima: {ts.temperatura_minima}")
        print(f"    Factor de enfriamiento: {ts.factor_enfriamiento}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error en algoritmo: {e}")
        return False


def prueba_rapida():
    """Ejecuta una prueba rápida de generación de recomendaciones."""
    print("\n" + "="*80)
    print("6. PRUEBA RÁPIDA DE GENERACIÓN DE RECOMENDACIONES")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
        from server.models.agente_recomendador import AgenteRecomendador
        
        agente = AgenteRecomendador('SUC001')
        print(f"  Generando recomendación para 100 Bs...")
        
        resultado = agente.generar_recomendaciones(presupuesto=100.0)
        
        print(f"  ✓ Recomendaciones generadas exitosamente")
        print(f"    Sucursal: {resultado['sucursal_nombre']}")
        print(f"    Recomendaciones: {len(resultado['recomendaciones'])}")
        
        for rec in resultado['recomendaciones']:
            print(f"      • {rec['tipo']}: {rec['total']} Bs. ({rec['cantidad_productos_diferentes']} productos)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def mostrar_resumen(resultados):
    """Muestra un resumen de los resultados."""
    print("\n" + "="*80)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*80)
    
    total = len(resultados)
    exitosos = sum(resultados.values())
    
    print(f"\nPruebas completadas: {exitosos}/{total}")
    
    for nombre, resultado in resultados.items():
        simbolo = "✓" if resultado else "✗"
        print(f"  {simbolo} {nombre}")
    
    if exitosos == total:
        print("\n" + "="*80)
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("="*80)
        print("\nPróximos pasos:")
        print("  1. Iniciar el servidor: cd server && python app.py")
        print("  2. Ejecutar pruebas completas: python test_agente_recomendador.py")
        print("  3. Probar API: python ejemplos_api.py")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("="*80)
        print("\nRevisar los errores arriba y:")
        print("  1. Verificar que todos los archivos existan")
        print("  2. Instalar dependencias: pip install -r server/requirements.txt")
        print("  3. Verificar la estructura de los inventarios")
        print("="*80 + "\n")


if __name__ == '__main__':
    print("\n🔍 VERIFICACIÓN DEL SISTEMA MULTI-AGENTE")
    print("="*80 + "\n")
    
    resultados = {}
    
    resultados["Estructura de archivos"] = verificar_estructura_archivos()
    resultados["Dependencias de Python"] = verificar_dependencias()
    resultados["Inventarios"] = verificar_inventarios()
    resultados["Importación del agente"] = verificar_importacion_agente()
    resultados["Algoritmo Temple Simulado"] = verificar_algoritmo()
    resultados["Prueba de recomendaciones"] = prueba_rapida()
    
    mostrar_resumen(resultados)
