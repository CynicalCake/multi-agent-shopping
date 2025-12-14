"""
Ejemplos de uso de la API del Agente Comprador
Requiere que el servidor esté corriendo: cd server && python app.py
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'


def ejemplo_1_obtener_mapa():
    """Ejemplo 1: Obtener mapa de una sucursal"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Obtener mapa de sucursal")
    print("="*80)
    
    response = requests.get(f'{BASE_URL}/sucursal/SUC001/mapa')
    data = response.json()
    
    print(f"\nSucursal: {data['nombre']}")
    print(f"Dimensiones: {data['dimensiones']['filas']}x{data['dimensiones']['columnas']}")
    print(f"Entrada: {data['entrada']}")
    print(f"Caja: {data['caja']}")
    print(f"Zonas de productos: {len(data['zonas_productos'])}")
    print(f"Obstáculos: {len(data['obstaculos'])}")
    print(f"Pasillos: {len(data['pasillos'])}")
    
    print("\nPrimeras 5 zonas de productos:")
    for prod_id, zona in list(data['zonas_productos'].items())[:5]:
        print(f"  Producto {prod_id}: {zona}")


def ejemplo_2_crear_comprador():
    """Ejemplo 2: Crear un agente comprador"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Crear agente comprador")
    print("="*80)
    
    data = {
        'sucursal_id': 'SUC001'
    }
    
    response = requests.post(f'{BASE_URL}/comprador/crear', json=data)
    result = response.json()
    
    print(f"\nComprador creado: {result['comprador_id']}")
    print(f"Sucursal: {result['sucursal_nombre']}")
    print(f"Estado: {result['estado']}")
    print(f"Posición inicial: {result['posicion_actual']}")
    
    return result['comprador_id']


def ejemplo_3_compra_manual(comprador_id):
    """Ejemplo 3: Proceso de compra manual (paso a paso)"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Compra manual paso a paso")
    print("="*80)
    
    # 1. Planificar compra
    print("\n1. Planificando compra...")
    lista_compras = [
        {'id': 1, 'nombre': 'Leche Entera 1L', 'cantidad': 2},
        {'id': 3, 'nombre': 'Arroz Blanco 1kg', 'cantidad': 1},
        {'id': 9, 'nombre': 'Detergente Líquido 1L', 'cantidad': 1}
    ]
    
    data = {
        'comprador_id': comprador_id,
        'sucursal_id': 'SUC001',
        'lista_compras': lista_compras
    }
    
    response = requests.post(f'{BASE_URL}/comprador/iniciar_compra', json=data)
    result = response.json()
    
    print(f"  Estado: {result['estado']}")
    print(f"  Productos en lista: {result['estado']['productos_en_lista']}")
    print(f"  Distancia planificada: {result['estado']['distancia_recorrida']} pasos")
    
    # 2. Ejecutar compra
    print("\n2. Ejecutando compra...")
    data = {'comprador_id': comprador_id}
    response = requests.post(f'{BASE_URL}/comprador/compra_completa', json=data)
    result = response.json()
    
    print(f"  Estado final: {result['estado']}")
    print(f"  Total items: {result['total_items']}")
    print(f"  Distancia total: {result['distancia_total']} pasos")
    print(f"  Tiempo estimado: {result['tiempo_estimado']}")
    
    print(f"\n  Productos recolectados:")
    for prod in result['productos_recolectados']:
        print(f"    • {prod['nombre']} x{prod['cantidad']}")
    
    print(f"\n  Primeros 10 pasos:")
    for paso in result['ruta_detallada'][:10]:
        print(f"    Paso {paso['paso']}: {paso['accion']} en {paso['posicion']}")


def ejemplo_4_flujo_completo():
    """Ejemplo 4: Flujo completo (Recomendador + Comprador)"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Flujo completo - Recomendación + Navegación")
    print("="*80)
    
    data = {
        'sucursal_id': 'SUC002',
        'presupuesto': 200.0,
        'categorias_preferidas': ['carnes', 'verduras', 'lacteos']
    }
    
    print(f"\nSolicitando flujo completo con presupuesto {data['presupuesto']} Bs.")
    print(f"Categorías preferidas: {', '.join(data['categorias_preferidas'])}")
    
    response = requests.post(f'{BASE_URL}/comprador/flujo_completo', json=data)
    result = response.json()
    
    # Recomendación
    rec = result['recomendacion']
    print(f"\n1. RECOMENDACIÓN:")
    print(f"   Total: {rec['total']} Bs.")
    print(f"   Productos: {len(rec['productos'])}")
    print(f"   Items: {rec['cantidad_items']}")
    
    print(f"\n   Primeros 5 productos:")
    for prod in rec['productos'][:5]:
        print(f"     • {prod['nombre']} x{prod['cantidad']} - {prod['subtotal']} Bs.")
    
    # Navegación
    nav = result['navegacion']
    print(f"\n2. NAVEGACIÓN:")
    print(f"   Distancia: {nav['distancia_total']} pasos")
    print(f"   Tiempo: {nav['tiempo_estimado']}")
    print(f"   Items recolectados: {nav['total_items']}")
    
    print(f"\n   Resumen de ruta:")
    print(f"     • Inicio: {nav['ruta_detallada'][0]['posicion']}")
    
    # Contar recogidas de productos
    recogidas = [p for p in nav['ruta_detallada'] if p['accion'] == 'recoger_producto']
    print(f"     • Productos recogidos: {len(recogidas)} paradas")
    
    print(f"     • Fin: {nav['ruta_detallada'][-1]['posicion']} (caja)")


def ejemplo_5_compra_grande():
    """Ejemplo 5: Compra grande con presupuesto alto"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Compra grande (presupuesto 500 Bs.)")
    print("="*80)
    
    data = {
        'sucursal_id': 'SUC001',
        'presupuesto': 500.0,
        'categorias_preferidas': ['limpieza', 'carnes', 'frutas', 'granos', 'bebidas']
    }
    
    print(f"\nSolicitando compra grande: {data['presupuesto']} Bs.")
    
    response = requests.post(f'{BASE_URL}/comprador/flujo_completo', json=data)
    result = response.json()
    
    rec = result['recomendacion']
    nav = result['navegacion']
    
    print(f"\nRECOMENDACIÓN:")
    print(f"  Total: {rec['total']} Bs.")
    print(f"  Productos diferentes: {len(rec['productos'])}")
    print(f"  Total items: {rec['cantidad_items']}")
    
    # Agrupar por categoría
    categorias = {}
    for prod in rec['productos']:
        cat = prod['categoria']
        if cat not in categorias:
            categorias[cat] = 0
        categorias[cat] += prod['cantidad']
    
    print(f"\n  Items por categoría:")
    for cat, cant in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"    {cat}: {cant} items")
    
    print(f"\nNAVEGACIÓN:")
    print(f"  Distancia: {nav['distancia_total']} pasos")
    print(f"  Tiempo: {nav['tiempo_estimado']}")
    
    # Calcular zonas visitadas
    zonas_visitadas = set()
    for paso in nav['ruta_detallada']:
        if paso['accion'] == 'recoger_producto':
            zonas_visitadas.add(tuple(paso['posicion']))
    
    print(f"  Zonas visitadas: {len(zonas_visitadas)}")
    print(f"  Paradas para recoger: {len([p for p in nav['ruta_detallada'] if p['accion'] == 'recoger_producto'])}")


def ejemplo_6_comparar_sucursales():
    """Ejemplo 6: Comparar misma compra en diferentes sucursales"""
    print("\n" + "="*80)
    print("EJEMPLO 6: Comparar sucursales")
    print("="*80)
    
    presupuesto = 150.0
    categorias = ['lacteos', 'panaderia', 'frutas']
    
    print(f"\nComparando compra de {presupuesto} Bs. en ambas sucursales")
    print(f"Categorías: {', '.join(categorias)}\n")
    
    for sucursal in ['SUC001', 'SUC002']:
        data = {
            'sucursal_id': sucursal,
            'presupuesto': presupuesto,
            'categorias_preferidas': categorias
        }
        
        response = requests.post(f'{BASE_URL}/comprador/flujo_completo', json=data)
        result = response.json()
        
        rec = result['recomendacion']
        nav = result['navegacion']
        
        print(f"{result['navegacion']['sucursal_nombre']}:")
        print(f"  Recomendación: {rec['total']} Bs., {len(rec['productos'])} productos, {rec['cantidad_items']} items")
        print(f"  Navegación: {nav['distancia_total']} pasos, {nav['tiempo_estimado']}")
        print()


if __name__ == '__main__':
    print("\n🛒 EJEMPLOS DE USO DE LA API DEL AGENTE COMPRADOR")
    print("="*80)
    print("\nAsegúrate de que el servidor esté corriendo:")
    print("  cd server && python app.py")
    print("\nPresiona Enter para continuar...")
    input()
    
    try:
        # Ejemplo 1: Obtener mapa
        ejemplo_1_obtener_mapa()
        input("\nPresiona Enter para continuar...")
        
        # Ejemplo 2: Crear comprador
        comprador_id = ejemplo_2_crear_comprador()
        input("\nPresiona Enter para continuar...")
        
        # Ejemplo 3: Compra manual
        ejemplo_3_compra_manual(comprador_id)
        input("\nPresiona Enter para continuar...")
        
        # Ejemplo 4: Flujo completo
        ejemplo_4_flujo_completo()
        input("\nPresiona Enter para continuar...")
        
        # Ejemplo 5: Compra grande
        ejemplo_5_compra_grande()
        input("\nPresiona Enter para continuar...")
        
        # Ejemplo 6: Comparar sucursales
        ejemplo_6_comparar_sucursales()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté corriendo:")
        print("  cd server && python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
