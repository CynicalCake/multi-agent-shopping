"""
Agente Recomendador
Este agente es responsable de generar listas de compras optimizadas
basadas en presupuesto y preferencias del usuario.
"""

import json
import os
from typing import List, Dict, Optional
from utils.algoritmos_busqueda import TempleSimulado


class AgenteRecomendador:
    """
    Agente inteligente que recomienda listas de compras utilizando Temple Simulado.
    Cada instancia está asociada a una sucursal específica.
    """
    
    def __init__(self, sucursal_id: str):
        """
        Inicializa el agente recomendador para una sucursal específica.
        
        Args:
            sucursal_id: Identificador único de la sucursal
        """
        self.sucursal_id = sucursal_id
        self.inventario = self._cargar_inventario()
        self.nombre_sucursal = self.inventario.get('nombre', f'Sucursal {sucursal_id}')
        self.productos = self.inventario.get('productos', [])
        self.temple_simulado = TempleSimulado(
            temperatura_inicial=1000.0,
            temperatura_minima=1.0,
            factor_enfriamiento=0.95,
            iteraciones_por_temperatura=100
        )
        self.estado = "activo"
        print(f"[Agente Recomendador] Inicializado para {self.nombre_sucursal} ({sucursal_id})")
        print(f"[Agente Recomendador] Productos disponibles: {len(self.productos)}")
    
    def _cargar_inventario(self) -> Dict:
        """
        Carga el inventario de la sucursal desde el archivo JSON.
        
        Returns:
            Diccionario con la información del inventario
        """
        ruta_inventario = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'inventario', f'{self.sucursal_id}.json'
        )
        
        try:
            with open(ruta_inventario, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            print(f"[ERROR] No se encontró el inventario para {self.sucursal_id}")
            return {'productos': []}
        except json.JSONDecodeError:
            print(f"[ERROR] Error al decodificar el inventario para {self.sucursal_id}")
            return {'productos': []}
    
    def filtrar_por_categorias(
        self, 
        categorias_preferidas: Optional[List[str]]
    ) -> List[Dict]:
        """
        Filtra productos según categorías preferidas, pero mantiene todos disponibles.
        
        Args:
            categorias_preferidas: Lista de categorías solicitadas por el usuario
            
        Returns:
            Lista de productos (todos, pero priorizando las categorías)
        """
        if not categorias_preferidas:
            return self.productos
        
        # Retornar todos los productos, el algoritmo de Temple Simulado
        # se encargará de priorizar las categorías mediante la función de costo
        return self.productos
    
    def generar_recomendaciones(
        self,
        presupuesto: float,
        categorias_preferidas: Optional[List[str]] = None
    ) -> Dict:
        """
        Genera tres listas de compras recomendadas: exacta, superior e inferior.
        
        Args:
            presupuesto: Presupuesto disponible del comprador
            categorias_preferidas: Categorías de productos preferidas (opcional)
            
        Returns:
            Diccionario con las tres recomendaciones y metadatos
        """
        print(f"\n[Agente Recomendador] Generando recomendaciones...")
        print(f"  Presupuesto: {presupuesto} Bs.")
        print(f"  Categorías preferidas: {categorias_preferidas or 'Ninguna'}")
        
        if categorias_preferidas is None:
            categorias_preferidas = []
        
        # Filtrar inventario según categorías
        inventario_filtrado = self.filtrar_por_categorias(categorias_preferidas)
        
        if not inventario_filtrado:
            return {
                "error": "No hay productos disponibles en el inventario",
                "recomendaciones": []
            }
        
        # Generar lista base usando Temple Simulado
        print("  Ejecutando Temple Simulado...")
        lista_base = self.temple_simulado.optimizar(
            inventario_filtrado,
            presupuesto,
            categorias_preferidas
        )
        
        # Generar tres variantes: exacta, superior e inferior
        recomendaciones = []
        
        # 1. Lista exacta (ajustar al presupuesto exacto)
        lista_exacta = self._ajustar_a_presupuesto_exacto(
            lista_base, presupuesto, inventario_filtrado
        )
        recomendaciones.append(self._formatear_recomendacion(
            lista_exacta, presupuesto, "exacta"
        ))
        
        # 2. Lista superior (2-5% más del presupuesto)
        presupuesto_superior = presupuesto * 1.03  # 3% más
        lista_superior = self.temple_simulado.optimizar(
            inventario_filtrado,
            presupuesto_superior,
            categorias_preferidas
        )
        recomendaciones.append(self._formatear_recomendacion(
            lista_superior, presupuesto, "superior"
        ))
        
        # 3. Lista inferior (2-5% menos del presupuesto)
        presupuesto_inferior = presupuesto * 0.97  # 3% menos
        lista_inferior = self.temple_simulado.optimizar(
            inventario_filtrado,
            presupuesto_inferior,
            categorias_preferidas
        )
        recomendaciones.append(self._formatear_recomendacion(
            lista_inferior, presupuesto, "inferior"
        ))
        
        print(f"  ✓ Recomendaciones generadas exitosamente")
        
        return {
            "sucursal_id": self.sucursal_id,
            "sucursal_nombre": self.nombre_sucursal,
            "presupuesto_solicitado": presupuesto,
            "categorias_preferidas": categorias_preferidas,
            "recomendaciones": recomendaciones
        }
    
    def _ajustar_a_presupuesto_exacto(
        self,
        lista_base: List[tuple],
        presupuesto: float,
        inventario: List[Dict],
        tolerancia: float = 0.5
    ) -> List[tuple]:
        """
        Ajusta una lista de compras para que esté lo más cerca posible del presupuesto.
        
        Args:
            lista_base: Lista inicial de productos
            presupuesto: Presupuesto objetivo
            inventario: Inventario disponible
            tolerancia: Tolerancia aceptable en Bs.
            
        Returns:
            Lista ajustada
        """
        lista_ajustada = lista_base.copy()
        total_actual = sum(p['precio'] * c for p, c in lista_ajustada)
        
        intentos = 0
        max_intentos = 50
        
        while abs(total_actual - presupuesto) > tolerancia and intentos < max_intentos:
            intentos += 1
            
            if total_actual < presupuesto:
                # Agregar productos baratos o aumentar cantidades
                productos_baratos = [p for p in inventario if p['precio'] <= (presupuesto - total_actual)]
                if productos_baratos:
                    producto = min(productos_baratos, key=lambda p: abs(p['precio'] - (presupuesto - total_actual)))
                    lista_ajustada.append((producto, 1))
                    total_actual += producto['precio']
                else:
                    break
            else:
                # Quitar productos o reducir cantidades
                if lista_ajustada:
                    # Intentar reducir cantidad del producto más caro
                    lista_ajustada.sort(key=lambda x: x[0]['precio'] * x[1], reverse=True)
                    producto, cantidad = lista_ajustada[0]
                    
                    if cantidad > 1:
                        lista_ajustada[0] = (producto, cantidad - 1)
                        total_actual -= producto['precio']
                    else:
                        lista_ajustada.pop(0)
                        total_actual -= producto['precio']
                else:
                    break
        
        return lista_ajustada
    
    def _formatear_recomendacion(
        self,
        lista_productos: List[tuple],
        presupuesto_original: float,
        tipo: str
    ) -> Dict:
        """
        Formatea una lista de productos en el formato de salida JSON.
        
        Args:
            lista_productos: Lista de tuplas (producto, cantidad)
            presupuesto_original: Presupuesto solicitado por el usuario
            tipo: Tipo de recomendación ('exacta', 'superior', 'inferior')
            
        Returns:
            Diccionario con la recomendación formateada
        """
        productos_formateados = []
        total = 0.0
        
        # Consolidar productos repetidos
        productos_consolidados = {}
        for producto, cantidad in lista_productos:
            prod_id = producto['id']
            if prod_id in productos_consolidados:
                productos_consolidados[prod_id]['cantidad'] += cantidad
            else:
                productos_consolidados[prod_id] = {
                    'id': prod_id,
                    'nombre': producto['nombre'],
                    'precio_unitario': producto['precio'],
                    'cantidad': cantidad,
                    'categoria': producto['categoria']
                }
        
        # Formatear y calcular total
        for prod_id, datos in productos_consolidados.items():
            subtotal = datos['precio_unitario'] * datos['cantidad']
            productos_formateados.append({
                'id': datos['id'],
                'nombre': datos['nombre'],
                'precio_unitario': datos['precio_unitario'],
                'cantidad': datos['cantidad'],
                'categoria': datos['categoria'],
                'subtotal': round(subtotal, 2)
            })
            total += subtotal
        
        # Ordenar por categoría y nombre
        productos_formateados.sort(key=lambda p: (p['categoria'], p['nombre']))
        
        # Calcular diferencia y mensaje
        diferencia = round(total - presupuesto_original, 2)
        
        if tipo == "exacta":
            mensaje = f"Lista ajustada a tu presupuesto (diferencia: {abs(diferencia)} Bs.)"
        elif tipo == "superior":
            if diferencia > 0:
                mensaje = f"Te faltan {abs(diferencia)} Bs. para completar esta compra"
            else:
                mensaje = f"Lista ligeramente superior a tu presupuesto"
        else:  # inferior
            if diferencia < 0:
                mensaje = f"Con esta lista te sobrarán {abs(diferencia)} Bs."
            else:
                mensaje = f"Lista ajustada por debajo de tu presupuesto"
        
        return {
            'tipo': tipo,
            'total': round(total, 2),
            'diferencia': diferencia,
            'porcentaje_diferencia': round((diferencia / presupuesto_original) * 100, 2),
            'productos': productos_formateados,
            'cantidad_items': sum(p['cantidad'] for p in productos_formateados),
            'cantidad_productos_diferentes': len(productos_formateados),
            'mensaje': mensaje
        }
    
    def obtener_estado(self) -> Dict:
        """
        Retorna el estado actual del agente.
        
        Returns:
            Diccionario con información del estado del agente
        """
        return {
            'sucursal_id': self.sucursal_id,
            'sucursal_nombre': self.nombre_sucursal,
            'estado': self.estado,
            'productos_disponibles': len(self.productos),
            'categorias_disponibles': list(set(p['categoria'] for p in self.productos))
        }
    
    def obtener_inventario(self) -> Dict:
        """
        Retorna el inventario completo de la sucursal.
        
        Returns:
            Diccionario con el inventario
        """
        return self.inventario
