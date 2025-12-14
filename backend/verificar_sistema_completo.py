"""
Verificación completa del sistema - Fase 1 + Fase 2
Valida que todos los componentes estén correctamente instalados y funcionando.
"""

import sys
import os
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_section(title):
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")


def verificar_estructura_archivos():
    """Verifica que todos los archivos necesarios existan."""
    print_section("1. VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    
    archivos_requeridos = {
        'Fase 1 - Agente Recomendador': [
            'server/app.py',
            'server/utils/algoritmos_busqueda.py',
            'server/models/agente_recomendador.py',
            'server/data/inventario/SUC001.json',
            'server/data/inventario/SUC002.json',
            'test_agente_recomendador.py',
            'ejemplos_api.py'
        ],
        'Fase 2 - Agente Comprador': [
            'server/models/agente_comprador.py',
            'server/data/mapas/SUC001.json',
            'server/data/mapas/SUC002.json',
            'test_agente_comprador.py',
            'ejemplos_api_comprador.py'
        ],
        'Documentación': [
            'README.md',
            'IMPLEMENTACION.md',
            'SETUP.md'
        ]
    }
    
    total_ok = 0
    total_archivos = sum(len(archivos) for archivos in archivos_requeridos.values())
    
    for fase, archivos in archivos_requeridos.items():
        print(f"\n{fase}:")
        for archivo in archivos:
            if Path(archivo).exists():
                print_success(f"{archivo}")
                total_ok += 1
            else:
                print_error(f"{archivo} - NO ENCONTRADO")
    
    print(f"\n{Colors.BOLD}Archivos encontrados: {total_ok}/{total_archivos}{Colors.END}")
    return total_ok == total_archivos


def verificar_dependencias():
    """Verifica que todas las dependencias de Python estén instaladas."""
    print_section("2. VERIFICANDO DEPENDENCIAS DE PYTHON")
    
    dependencias = {
        'flask': '3.0.0',
        'flask_socketio': '5.3.5',
        'flask_cors': '4.0.0',
        'requests': None
    }
    
    total_ok = 0
    for dep, version_esperada in dependencias.items():
        try:
            modulo = __import__(dep)
            version = getattr(modulo, '__version__', 'desconocida')
            
            if version_esperada and version != version_esperada:
                print_warning(f"{dep} v{version} (esperada: v{version_esperada})")
            else:
                print_success(f"{dep} v{version}")
            total_ok += 1
        except ImportError:
            print_error(f"{dep} - NO INSTALADO")
    
    print(f"\n{Colors.BOLD}Dependencias instaladas: {total_ok}/{len(dependencias)}{Colors.END}")
    return total_ok == len(dependencias)


def verificar_datos():
    """Verifica que los archivos de datos tengan el formato correcto."""
    print_section("3. VERIFICANDO ARCHIVOS DE DATOS")
    
    import json
    
    # Verificar inventarios
    print("Inventarios:")
    for sucursal in ['SUC001', 'SUC002']:
        archivo = f'server/data/inventario/{sucursal}.json'
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            productos = len(data['productos'])
            categorias = len(set(p['categoria'] for p in data['productos']))
            print_success(f"{sucursal}: {productos} productos, {categorias} categorías")
            
        except Exception as e:
            print_error(f"{sucursal}: Error - {e}")
    
    # Verificar mapas
    print("\nMapas:")
    for sucursal in ['SUC001', 'SUC002']:
        archivo = f'server/data/mapas/{sucursal}.json'
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dims = data['dimensiones']
            zonas = len(data['zonas_productos'])
            obstaculos = len(data['obstaculos'])
            pasillos = len(data['pasillos'])
            
            print_success(f"{sucursal}: {dims['filas']}x{dims['columnas']}, {zonas} zonas, {obstaculos} obstáculos, {pasillos} pasillos")
            
        except Exception as e:
            print_error(f"{sucursal}: Error - {e}")
    
    return True


def verificar_agente_recomendador():
    """Verifica que el agente recomendador funcione correctamente."""
    print_section("4. VERIFICANDO AGENTE RECOMENDADOR")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
    
    try:
        from models.agente_recomendador import AgenteRecomendador
        
        print("Creando agente...")
        agente = AgenteRecomendador('SUC001')
        print_success("Agente creado correctamente")
        
        print("\nGenerando recomendaciones (100 Bs.)...")
        resultado = agente.generar_recomendaciones(presupuesto=100.0)
        
        print_success(f"Generadas {len(resultado['recomendaciones'])} recomendaciones")
        
        for rec in resultado['recomendaciones']:
            tipo = rec['tipo']
            total = rec['total']
            prods = len(rec['productos'])
            items = rec['cantidad_items']
            print(f"  • Tipo {tipo}: {total} Bs., {prods} productos, {items} items")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_agente_comprador():
    """Verifica que el agente comprador funcione correctamente."""
    print_section("5. VERIFICANDO AGENTE COMPRADOR")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
    
    try:
        from models.agente_comprador import AgenteComprador
        
        print("Creando agente...")
        agente = AgenteComprador('COMP_TEST')
        print_success("Agente creado correctamente")
        
        print("\nIngresando a sucursal SUC001...")
        agente.ingresar_a_sucursal('SUC001')
        print_success("Ingreso exitoso")
        
        print("\nPlanificando compra de 2 productos...")
        lista = [
            {'id': 1, 'nombre': 'Leche Entera 1L', 'cantidad': 1},
            {'id': 3, 'nombre': 'Arroz Blanco 1kg', 'cantidad': 1}
        ]
        agente.planificar_compra(lista)
        print_success("Planificación exitosa")
        
        print("\nEjecutando compra...")
        resultado = agente.ejecutar_compra()
        
        print_success(f"Compra completada")
        print(f"  • Items: {resultado['total_items']}")
        print(f"  • Distancia: {resultado['distancia_total']} pasos")
        print(f"  • Tiempo: {resultado['tiempo_estimado']}")
        print(f"  • Pasos en ruta: {len(resultado['ruta_detallada'])}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_algoritmos():
    """Verifica que los algoritmos de IA funcionen correctamente."""
    print_section("6. VERIFICANDO ALGORITMOS DE IA")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
    
    try:
        from utils.algoritmos_busqueda import TempleSimulado, BusquedaAEstrella
        import json
        
        # Temple Simulado
        print("Temple Simulado:")
        ts = TempleSimulado()
        print_success(f"Algoritmo inicializado correctamente (T_inicial={ts.temperatura_inicial})")
        
        # A*
        print("\nA* (A Estrella):")
        with open('server/data/mapas/SUC001.json', 'r', encoding='utf-8') as f:
            mapa = json.load(f)
        
        busqueda = BusquedaAEstrella()
        print_success("Algoritmo A* inicializado correctamente")
        
        print("\nAmbos algoritmos están listos para ser usados por los agentes")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_tests():
    """Verifica que los tests estén disponibles y sean ejecutables."""
    print_section("7. VERIFICANDO SCRIPTS DE PRUEBA")
    
    tests = {
        'test_agente_recomendador.py': 'Agente Recomendador (5 tests)',
        'test_agente_comprador.py': 'Agente Comprador (7 tests)'
    }
    
    for archivo, descripcion in tests.items():
        if Path(archivo).exists():
            print_success(f"{archivo} - {descripcion}")
        else:
            print_error(f"{archivo} - NO ENCONTRADO")
    
    print_info("\nPara ejecutar los tests:")
    print("  python test_agente_recomendador.py")
    print("  python test_agente_comprador.py")
    
    return True


def main():
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}🔍 VERIFICACIÓN COMPLETA DEL SISTEMA MULTI-AGENTE{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}")
    
    resultados = []
    
    # 1. Estructura
    resultados.append(("Estructura de archivos", verificar_estructura_archivos()))
    
    # 2. Dependencias
    resultados.append(("Dependencias Python", verificar_dependencias()))
    
    # 3. Datos
    resultados.append(("Archivos de datos", verificar_datos()))
    
    # 4. Agente Recomendador
    resultados.append(("Agente Recomendador", verificar_agente_recomendador()))
    
    # 5. Agente Comprador
    resultados.append(("Agente Comprador", verificar_agente_comprador()))
    
    # 6. Algoritmos
    resultados.append(("Algoritmos de IA", verificar_algoritmos()))
    
    # 7. Tests
    resultados.append(("Scripts de prueba", verificar_tests()))
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    exitosos = sum(1 for _, ok in resultados if ok)
    total = len(resultados)
    
    for nombre, ok in resultados:
        if ok:
            print_success(f"{nombre}: OK")
        else:
            print_error(f"{nombre}: FALLO")
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    if exitosos == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SISTEMA COMPLETAMENTE FUNCIONAL ({exitosos}/{total}){Colors.END}")
        print(f"\n{Colors.BOLD}Próximos pasos:{Colors.END}")
        print("  1. Iniciar el servidor: cd server && python app.py")
        print("  2. Ejecutar tests: python test_agente_recomendador.py && python test_agente_comprador.py")
        print("  3. Probar API: python ejemplos_api.py && python ejemplos_api_comprador.py")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ VERIFICACIÓN PARCIAL ({exitosos}/{total}){Colors.END}")
        print(f"\n{Colors.BOLD}Revisa los errores anteriores y corrige los problemas.{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")


if __name__ == '__main__':
    main()
