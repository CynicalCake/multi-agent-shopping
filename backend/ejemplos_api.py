"""
Ejemplos de uso de la API del Sistema Multi-Agente
Muestra cómo consumir la API REST y WebSockets
"""

import requests
import json

# URL base del servidor (ajusta si es necesario)
BASE_URL = "http://localhost:5000"


def ejemplo_1_listar_sucursales():
    """Ejemplo 1: Listar todas las sucursales disponibles."""
    print("\n" + "="*80)
    print("EJEMPLO 1: Listar sucursales disponibles")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/sucursales")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal de sucursales: {data['total']}")
        for sucursal in data['sucursales']:
            print(f"\n  {sucursal['nombre']} ({sucursal['sucursal_id']})")
            print(f"  - Productos disponibles: {sucursal['productos_disponibles']}")
            print(f"  - Estado: {sucursal['estado']}")
    else:
        print(f"Error: {response.status_code}")


def ejemplo_2_obtener_inventario():
    """Ejemplo 2: Obtener el inventario de una sucursal."""
    print("\n" + "="*80)
    print("EJEMPLO 2: Obtener inventario de SUC001")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/sucursal/SUC001/inventario")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSucursal: {data['nombre']}")
        print(f"Total de productos: {len(data['productos'])}")
        
        # Mostrar primeros 5 productos
        print("\nPrimeros 5 productos:")
        for producto in data['productos'][:5]:
            print(f"  - {producto['nombre']}: {producto['precio']} Bs.")
            print(f"    Categoría: {producto['categoria']} | Importancia: {producto['importancia']}")
    else:
        print(f"Error: {response.status_code}")


def ejemplo_3_solicitar_recomendacion_basica():
    """Ejemplo 3: Solicitar recomendación básica sin categorías."""
    print("\n" + "="*80)
    print("EJEMPLO 3: Solicitar recomendación básica (100 Bs.)")
    print("="*80)
    
    payload = {
        "sucursal_id": "SUC001",
        "presupuesto": 100.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recomendador/solicitar",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSucursal: {data['sucursal_nombre']}")
        print(f"Presupuesto solicitado: {data['presupuesto_solicitado']} Bs.")
        
        for i, rec in enumerate(data['recomendaciones'], 1):
            print(f"\n  Recomendación {i} ({rec['tipo']})")
            print(f"  - Total: {rec['total']} Bs.")
            print(f"  - Diferencia: {rec['diferencia']:+.2f} Bs.")
            print(f"  - Productos: {rec['cantidad_productos_diferentes']}")
            print(f"  - Mensaje: {rec['mensaje']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def ejemplo_4_solicitar_recomendacion_con_categorias():
    """Ejemplo 4: Solicitar recomendación con categorías preferidas."""
    print("\n" + "="*80)
    print("EJEMPLO 4: Solicitar recomendación con categorías (200 Bs.)")
    print("="*80)
    
    payload = {
        "sucursal_id": "SUC002",
        "presupuesto": 200.0,
        "categorias_preferidas": ["lacteos", "panaderia", "verduras"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recomendador/solicitar",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSucursal: {data['sucursal_nombre']}")
        print(f"Presupuesto: {data['presupuesto_solicitado']} Bs.")
        print(f"Categorías preferidas: {', '.join(data['categorias_preferidas'])}")
        
        # Mostrar solo la recomendación exacta
        rec_exacta = next(r for r in data['recomendaciones'] if r['tipo'] == 'exacta')
        print(f"\nRecomendación EXACTA:")
        print(f"  Total: {rec_exacta['total']} Bs.")
        print(f"  Productos en la lista:")
        for prod in rec_exacta['productos']:
            print(f"    • {prod['nombre']} x{prod['cantidad']} - {prod['subtotal']} Bs.")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def ejemplo_5_estado_recomendador():
    """Ejemplo 5: Consultar el estado de un agente recomendador."""
    print("\n" + "="*80)
    print("EJEMPLO 5: Consultar estado del agente recomendador")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/recomendador/estado/SUC001")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAgente Recomendador: {data['sucursal_nombre']}")
        print(f"  - Estado: {data['estado']}")
        print(f"  - Productos disponibles: {data['productos_disponibles']}")
        print(f"  - Categorías disponibles:")
        for categoria in sorted(data['categorias_disponibles']):
            print(f"    • {categoria}")
    else:
        print(f"Error: {response.status_code}")


def ejemplo_6_comparar_sucursales():
    """Ejemplo 6: Comparar recomendaciones de ambas sucursales."""
    print("\n" + "="*80)
    print("EJEMPLO 6: Comparar recomendaciones de SUC001 vs SUC002")
    print("="*80)
    
    presupuesto = 150.0
    categorias = ["lacteos", "granos"]
    
    for sucursal_id in ["SUC001", "SUC002"]:
        payload = {
            "sucursal_id": sucursal_id,
            "presupuesto": presupuesto,
            "categorias_preferidas": categorias
        }
        
        response = requests.post(
            f"{BASE_URL}/api/recomendador/solicitar",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            rec_exacta = next(r for r in data['recomendaciones'] if r['tipo'] == 'exacta')
            
            print(f"\n{data['sucursal_nombre']}:")
            print(f"  Total: {rec_exacta['total']} Bs.")
            print(f"  Items: {rec_exacta['cantidad_items']}")
            print(f"  Productos diferentes: {rec_exacta['cantidad_productos_diferentes']}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("EJEMPLOS DE USO DE LA API - Sistema Multi-Agente de Supermercado")
    print("="*80)
    print("\nAsegúrate de que el servidor esté ejecutándose en http://localhost:5000")
    print("Ejecuta: cd server && python app.py")
    print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
    
    try:
        input()
        
        # Ejecutar todos los ejemplos
        ejemplo_1_listar_sucursales()
        ejemplo_2_obtener_inventario()
        ejemplo_3_solicitar_recomendacion_basica()
        ejemplo_4_solicitar_recomendacion_con_categorias()
        ejemplo_5_estado_recomendador()
        ejemplo_6_comparar_sucursales()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS EJEMPLOS EJECUTADOS CORRECTAMENTE")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
        print("Ejecuta: cd server && python app.py")
    except KeyboardInterrupt:
        print("\n\nEjecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
