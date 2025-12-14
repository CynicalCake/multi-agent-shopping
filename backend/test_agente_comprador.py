"""
Script de prueba para el Agente Comprador
Valida la funcionalidad del agente de navegación y compra.
"""

import sys
import os

# Agregar el directorio server al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from models.agente_comprador import AgenteComprador
from models.agente_recomendador import AgenteRecomendador


def test_ingreso_a_sucursal():
    """Test 1: Ingreso básico a una sucursal."""
    print("\n" + "="*80)
    print("TEST 1: Ingreso a sucursal")
    print("="*80)
    
    comprador = AgenteComprador('COMP001')
    comprador.ingresar_a_sucursal('SUC001')
    
    estado = comprador.obtener_estado()
    
    print(f"\nComprador: {estado['comprador_id']}")
    print(f"Estado: {estado['estado']}")
    print(f"Sucursal: {estado['sucursal_nombre']}")
    print(f"Posición actual: {estado['posicion_actual']}")
    
    assert estado['estado'] == 'en_sucursal'
    assert estado['sucursal_id'] == 'SUC001'
    print("\n✅ Test completado exitosamente")
    print("="*80)


def test_planificacion_simple():
    """Test 2: Planificación de compra simple."""
    print("\n" + "="*80)
    print("TEST 2: Planificación de compra simple")
    print("="*80)
    
    comprador = AgenteComprador('COMP002')
    comprador.ingresar_a_sucursal('SUC001')
    
    # Lista de compras simple
    lista_compras = [
        {'id': 1, 'nombre': 'Leche Entera 1L', 'cantidad': 2},
        {'id': 2, 'nombre': 'Pan Integral 500g', 'cantidad': 1}
    ]
    
    comprador.planificar_compra(lista_compras)
    
    estado = comprador.obtener_estado()
    
    print(f"\nProductos en lista: {estado['productos_en_lista']}")
    print(f"Productos recolectados: {estado['productos_recolectados']}")
    print(f"Distancia planificada: {estado['distancia_recorrida']} pasos")
    
    assert estado['estado'] == 'comprando'
    assert estado['productos_en_lista'] == 2
    print("\n✅ Test completado exitosamente")
    print("="*80)


def test_ejecucion_compra():
    """Test 3: Ejecución completa de compra."""
    print("\n" + "="*80)
    print("TEST 3: Ejecución completa de compra")
    print("="*80)
    
    comprador = AgenteComprador('COMP003')
    comprador.ingresar_a_sucursal('SUC001')
    
    lista_compras = [
        {'id': 1, 'nombre': 'Leche Entera 1L', 'cantidad': 2},
        {'id': 3, 'nombre': 'Arroz Blanco 1kg', 'cantidad': 1},
        {'id': 10, 'nombre': 'Papel Higiénico x4', 'cantidad': 1}
    ]
    
    comprador.planificar_compra(lista_compras)
    resultado = comprador.ejecutar_compra()
    
    print(f"\nSucursal: {resultado['sucursal_nombre']}")
    print(f"Total de items: {resultado['total_items']}")
    print(f"Distancia recorrida: {resultado['distancia_total']} pasos")
    print(f"Tiempo estimado: {resultado['tiempo_estimado']}")
    print(f"Estado final: {resultado['estado']}")
    
    print(f"\nProductos recolectados:")
    for prod in resultado['productos_recolectados']:
        print(f"  • {prod['nombre']} x{prod['cantidad']}")
    
    print(f"\nPrimeros 10 pasos de la ruta:")
    for paso in resultado['ruta_detallada'][:10]:
        accion = paso['accion']
        pos = paso['posicion']
        desc = paso.get('descripcion', '')
        print(f"  Paso {paso['paso']}: {accion} en {pos} {desc}")
    
    assert resultado['estado'] == 'finalizado'
    assert resultado['total_items'] == 4
    print("\n✅ Test completado exitosamente")
    print("="*80)


def test_integracion_con_recomendador():
    """Test 4: Integración con el agente recomendador."""
    print("\n" + "="*80)
    print("TEST 4: Integración con agente recomendador")
    print("="*80)
    
    # 1. Obtener recomendación
    print("\n1. Solicitando recomendación...")
    recomendador = AgenteRecomendador('SUC001')
    recomendaciones = recomendador.generar_recomendaciones(
        presupuesto=150.0,
        categorias_preferidas=['lacteos', 'verduras']
    )
    
    rec_exacta = next(r for r in recomendaciones['recomendaciones'] if r['tipo'] == 'exacta')
    
    print(f"  Recomendación recibida: {len(rec_exacta['productos'])} productos")
    print(f"  Total: {rec_exacta['total']} Bs.")
    
    # 2. Crear comprador y ejecutar compra
    print("\n2. Ejecutando compra con la recomendación...")
    comprador = AgenteComprador('COMP004')
    comprador.ingresar_a_sucursal('SUC001')
    comprador.planificar_compra(rec_exacta['productos'])
    resultado = comprador.ejecutar_compra()
    
    print(f"\n3. Resultado de la compra:")
    print(f"  Items recolectados: {resultado['total_items']}")
    print(f"  Distancia: {resultado['distancia_total']} pasos")
    print(f"  Tiempo: {resultado['tiempo_estimado']}")
    
    print(f"\n4. Resumen de productos:")
    for prod in resultado['productos_recolectados'][:5]:
        print(f"  • {prod['nombre']} x{prod['cantidad']}")
    
    if len(resultado['productos_recolectados']) > 5:
        print(f"  ... y {len(resultado['productos_recolectados']) - 5} más")
    
    assert resultado['estado'] == 'finalizado'
    print("\n✅ Test completado exitosamente")
    print("="*80)


def test_multiples_productos_misma_zona():
    """Test 5: Compra de múltiples productos en la misma zona."""
    print("\n" + "="*80)
    print("TEST 5: Múltiples productos en la misma zona")
    print("="*80)
    
    comprador = AgenteComprador('COMP005')
    comprador.ingresar_a_sucursal('SUC002')
    
    # Varios productos de lácteos (misma zona)
    lista_compras = [
        {'id': 1, 'nombre': 'Leche Descremada 1L', 'cantidad': 2},
        {'id': 5, 'nombre': 'Huevos Orgánicos x12', 'cantidad': 1},
        {'id': 12, 'nombre': 'Yogurt Griego 500ml', 'cantidad': 1},
        {'id': 13, 'nombre': 'Queso Mozzarella 400g', 'cantidad': 1}
    ]
    
    comprador.planificar_compra(lista_compras)
    resultado = comprador.ejecutar_compra()
    
    print(f"\nProductos solicitados: {len(lista_compras)}")
    print(f"Productos recolectados: {len(resultado['productos_recolectados'])}")
    print(f"Total items: {resultado['total_items']}")
    print(f"Distancia: {resultado['distancia_total']} pasos")
    
    # Verificar que los productos recolectados están en la misma zona
    zonas_visitadas = set()
    for prod in resultado['productos_recolectados']:
        zona = tuple(prod['posicion'])
        zonas_visitadas.add(zona)
    
    print(f"Zonas visitadas: {len(zonas_visitadas)}")
    
    # Verificar que al menos se recolectaron productos
    assert len(resultado['productos_recolectados']) > 0, "Deberían haberse recolectado productos"
    # Si se recolectó más de un producto, verificar que están en la misma zona
    if len(resultado['productos_recolectados']) > 1:
        assert len(zonas_visitadas) == 1, f"Los {len(resultado['productos_recolectados'])} productos recolectados deberían estar en la misma zona"
    print("\n✅ Test completado exitosamente - Optimización de zona detectada")
    print("="*80)


def test_compra_grande():
    """Test 6: Compra con muchos productos (presupuesto alto)."""
    print("\n" + "="*80)
    print("TEST 6: Compra grande con presupuesto alto")
    print("="*80)
    
    # Obtener recomendación con presupuesto alto
    recomendador = AgenteRecomendador('SUC002')
    recomendaciones = recomendador.generar_recomendaciones(
        presupuesto=500.0,
        categorias_preferidas=['limpieza', 'carnes', 'frutas', 'granos']
    )
    
    rec_exacta = next(r for r in recomendaciones['recomendaciones'] if r['tipo'] == 'exacta')
    
    print(f"\nRecomendación con presupuesto 500 Bs:")
    print(f"  Productos: {len(rec_exacta['productos'])}")
    print(f"  Total: {rec_exacta['total']} Bs.")
    
    # Ejecutar compra
    comprador = AgenteComprador('COMP006')
    comprador.ingresar_a_sucursal('SUC002')
    comprador.planificar_compra(rec_exacta['productos'])
    resultado = comprador.ejecutar_compra()
    
    print(f"\nResultado de compra grande:")
    print(f"  Total items: {resultado['total_items']}")
    print(f"  Productos diferentes: {len(resultado['productos_recolectados'])}")
    print(f"  Distancia total: {resultado['distancia_total']} pasos")
    print(f"  Tiempo estimado: {resultado['tiempo_estimado']}")
    
    # Contar zonas visitadas
    zonas_visitadas = set()
    for paso in resultado['ruta_detallada']:
        if paso['accion'] == 'recoger_producto':
            zonas_visitadas.add(tuple(paso['posicion']))
    
    print(f"  Zonas visitadas: {len(zonas_visitadas)}")
    
    assert resultado['distancia_total'] > 0
    assert resultado['total_items'] > 10
    print("\n✅ Test completado exitosamente")
    print("="*80)


def test_visualizacion_ruta():
    """Test 7: Visualización básica de la ruta."""
    print("\n" + "="*80)
    print("TEST 7: Visualización de ruta")
    print("="*80)
    
    comprador = AgenteComprador('COMP007')
    comprador.ingresar_a_sucursal('SUC001')
    
    lista_compras = [
        {'id': 1, 'nombre': 'Leche Entera 1L', 'cantidad': 1},
        {'id': 9, 'nombre': 'Detergente Líquido 1L', 'cantidad': 1},
        {'id': 19, 'nombre': 'Manzanas 1kg', 'cantidad': 1}
    ]
    
    comprador.planificar_compra(lista_compras)
    resultado = comprador.ejecutar_compra()
    
    print(f"\nRuta completa ({len(resultado['ruta_detallada'])} pasos):")
    print("-" * 80)
    
    for paso in resultado['ruta_detallada']:
        accion = paso['accion']
        pos = paso['posicion']
        
        if accion == 'inicio':
            print(f"🏁 Paso {paso['paso']}: INICIO en {pos}")
        elif accion == 'recoger_producto':
            prod = paso['producto']
            print(f"🛒 Paso {paso['paso']}: RECOGER {prod['cantidad']}x {prod['nombre']} en {pos}")
        elif accion == 'caja':
            print(f"💰 Paso {paso['paso']}: CAJA en {pos}")
        elif paso['paso'] % 10 == 0:  # Mostrar cada 10 pasos
            print(f"   Paso {paso['paso']}: Avanzando por {pos}")
    
    print("-" * 80)
    print(f"\nResumen:")
    print(f"  Inicio: {resultado['ruta_detallada'][0]['posicion']}")
    print(f"  Fin: {resultado['ruta_detallada'][-1]['posicion']}")
    print(f"  Total pasos: {len(resultado['ruta_detallada'])}")
    
    print("\n✅ Test completado exitosamente")
    print("="*80)


if __name__ == '__main__':
    print("\nEJECUTANDO SUITE DE PRUEBAS DEL AGENTE COMPRADOR")
    print("="*80)
    
    try:
        test_ingreso_a_sucursal()
        test_planificacion_simple()
        test_ejecucion_compra()
        test_integracion_con_recomendador()
        test_multiples_productos_misma_zona()
        test_compra_grande()
        test_visualizacion_ruta()
        
        print("\n" + "="*80)
        print("✅ TODAS LAS PRUEBAS DEL AGENTE COMPRADOR COMPLETADAS EXITOSAMENTE")
        print("="*80)
        print("\n📊 Resumen:")
        print("  • Ingreso a sucursal: ✓")
        print("  • Planificación de compra: ✓")
        print("  • Ejecución de compra: ✓")
        print("  • Integración con recomendador: ✓")
        print("  • Optimización de zonas: ✓")
        print("  • Compras grandes: ✓")
        print("  • Visualización de rutas: ✓")
        print("\n" + "="*80 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ FALLO EN TEST: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
