"""
Script de prueba para el Agente Recomendador
Valida la funcionalidad del agente sin necesidad de iniciar el servidor.
"""

import sys
import os

# Agregar el directorio server al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from server.models.agente_recomendador import AgenteRecomendador


def imprimir_recomendacion(recomendacion, indice):
    """Imprime una recomendación de forma legible."""
    print(f"\n  {'='*70}")
    print(f"  RECOMENDACIÓN {indice}: {recomendacion['tipo'].upper()}")
    print(f"  {'='*70}")
    print(f"  Total: {recomendacion['total']} Bs.")
    print(f"  Diferencia: {recomendacion['diferencia']:+.2f} Bs. ({recomendacion['porcentaje_diferencia']:+.2f}%)")
    print(f"  Items: {recomendacion['cantidad_items']} | Productos diferentes: {recomendacion['cantidad_productos_diferentes']}")
    print(f"  Mensaje: {recomendacion['mensaje']}")
    print(f"\n  Productos:")
    print(f"  {'-'*70}")
    
    for producto in recomendacion['productos']:
        print(f"  • {producto['nombre']}")
        print(f"    Cantidad: {producto['cantidad']} | Precio unitario: {producto['precio_unitario']} Bs. | Subtotal: {producto['subtotal']} Bs.")
        print(f"    Categoría: {producto['categoria']}")


def test_recomendador_basico():
    """Prueba básica del agente recomendador."""
    print("\n" + "="*80)
    print("TEST 1: Recomendación básica sin categorías preferidas")
    print("="*80)
    
    agente = AgenteRecomendador('SUC001')
    
    presupuesto = 100.0
    resultado = agente.generar_recomendaciones(presupuesto=presupuesto)
    
    print(f"\nSucursal: {resultado['sucursal_nombre']}")
    print(f"Presupuesto solicitado: {resultado['presupuesto_solicitado']} Bs.")
    
    for i, recomendacion in enumerate(resultado['recomendaciones'], 1):
        imprimir_recomendacion(recomendacion, i)
    
    print("\n" + "="*80)


def test_recomendador_con_categorias():
    """Prueba del agente con categorías específicas."""
    print("\n" + "="*80)
    print("TEST 2: Recomendación con categorías preferidas (lacteos, panaderia)")
    print("="*80)
    
    agente = AgenteRecomendador('SUC001')
    
    presupuesto = 150.0
    categorias = ['lacteos', 'panaderia']
    resultado = agente.generar_recomendaciones(
        presupuesto=presupuesto,
        categorias_preferidas=categorias
    )
    
    print(f"\nSucursal: {resultado['sucursal_nombre']}")
    print(f"Presupuesto solicitado: {resultado['presupuesto_solicitado']} Bs.")
    print(f"Categorías preferidas: {', '.join(resultado['categorias_preferidas'])}")
    
    for i, recomendacion in enumerate(resultado['recomendaciones'], 1):
        imprimir_recomendacion(recomendacion, i)
    
    print("\n" + "="*80)


def test_recomendador_presupuesto_bajo():
    """Prueba con presupuesto bajo."""
    print("\n" + "="*80)
    print("TEST 3: Recomendación con presupuesto bajo (50 Bs.)")
    print("="*80)
    
    agente = AgenteRecomendador('SUC002')
    
    presupuesto = 50.0
    resultado = agente.generar_recomendaciones(presupuesto=presupuesto)
    
    print(f"\nSucursal: {resultado['sucursal_nombre']}")
    print(f"Presupuesto solicitado: {resultado['presupuesto_solicitado']} Bs.")
    
    for i, recomendacion in enumerate(resultado['recomendaciones'], 1):
        imprimir_recomendacion(recomendacion, i)
    
    print("\n" + "="*80)


def test_recomendador_presupuesto_alto():
    """Prueba con presupuesto alto."""
    print("\n" + "="*80)
    print("TEST 4: Recomendación con presupuesto alto (500 Bs.) - limpieza, carnes")
    print("="*80)
    
    agente = AgenteRecomendador('SUC002')
    
    presupuesto = 500.0
    categorias = ['limpieza', 'carnes']
    resultado = agente.generar_recomendaciones(
        presupuesto=presupuesto,
        categorias_preferidas=categorias
    )
    
    print(f"\nSucursal: {resultado['sucursal_nombre']}")
    print(f"Presupuesto solicitado: {resultado['presupuesto_solicitado']} Bs.")
    print(f"Categorías preferidas: {', '.join(resultado['categorias_preferidas'])}")
    
    for i, recomendacion in enumerate(resultado['recomendaciones'], 1):
        imprimir_recomendacion(recomendacion, i)
    
    print("\n" + "="*80)


def test_estado_inventario():
    """Prueba de consulta de estado e inventario."""
    print("\n" + "="*80)
    print("TEST 5: Consulta de estado e inventario")
    print("="*80)
    
    for sucursal_id in ['SUC001', 'SUC002']:
        agente = AgenteRecomendador(sucursal_id)
        estado = agente.obtener_estado()
        
        print(f"\n{estado['sucursal_nombre']} ({estado['sucursal_id']})")
        print(f"  Estado: {estado['estado']}")
        print(f"  Productos disponibles: {estado['productos_disponibles']}")
        print(f"  Categorías: {', '.join(sorted(estado['categorias_disponibles']))}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    print("\n🧪 EJECUTANDO SUITE DE PRUEBAS DEL AGENTE RECOMENDADOR")
    print("="*80)
    
    try:
        test_estado_inventario()
        test_recomendador_basico()
        test_recomendador_con_categorias()
        test_recomendador_presupuesto_bajo()
        test_recomendador_presupuesto_alto()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
