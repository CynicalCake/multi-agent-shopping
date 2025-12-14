"""
Agente Comprador
Este agente es responsable de navegar por la sucursal y recolectar productos
de manera eficiente usando planificación de rutas con A*.
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from utils.algoritmos_busqueda import BusquedaAEstrella


class AgenteComprador:
    """
    Agente inteligente que navega por una sucursal para recolectar productos.
    Utiliza A* para planificar rutas óptimas.
    """
    
    def __init__(self, comprador_id: str):
        """
        Inicializa el agente comprador.
        
        Args:
            comprador_id: Identificador único del comprador
        """
        self.comprador_id = comprador_id
        self.sucursal_id = None
        self.mapa_sucursal = None
        self.inventario_sucursal = None
        self.posicion_actual = None
        self.lista_compras = None
        self.productos_recolectados = []
        self.ruta_completa = []
        self.distancia_total = 0
        self.estado = "disponible"  # disponible, en_sucursal, comprando, finalizado
        self.a_estrella = BusquedaAEstrella()
        
        print(f"[Agente Comprador] Inicializado con ID: {comprador_id}")
    
    def _cargar_mapa(self, sucursal_id: str) -> Dict:
        """
        Carga el mapa de la sucursal desde el archivo JSON.
        
        Args:
            sucursal_id: Identificador de la sucursal
            
        Returns:
            Diccionario con la información del mapa
        """
        ruta_mapa = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'mapas', f'{sucursal_id}.json'
        )
        
        try:
            with open(ruta_mapa, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            raise ValueError(f"No se encontró el mapa para la sucursal {sucursal_id}")
        except json.JSONDecodeError:
            raise ValueError(f"Error al decodificar el mapa de {sucursal_id}")
    
    def _cargar_inventario(self, sucursal_id: str) -> Dict:
        """
        Carga el inventario de la sucursal desde el archivo JSON.
        
        Args:
            sucursal_id: Identificador de la sucursal
            
        Returns:
            Diccionario con la información del inventario
        """
        ruta_inventario = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'inventario', f'{sucursal_id}.json'
        )
        
        try:
            with open(ruta_inventario, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            raise ValueError(f"No se encontró el inventario para la sucursal {sucursal_id}")
        except json.JSONDecodeError:
            raise ValueError(f"Error al decodificar el inventario de {sucursal_id}")
    
    def ingresar_a_sucursal(self, sucursal_id: str):
        """
        El comprador ingresa a una sucursal.
        
        Args:
            sucursal_id: Identificador de la sucursal
        """
        print(f"\n[Agente Comprador {self.comprador_id}] Ingresando a sucursal {sucursal_id}...")
        
        # Cargar mapa e inventario
        self.sucursal_id = sucursal_id
        self.mapa_sucursal = self._cargar_mapa(sucursal_id)
        self.inventario_sucursal = self._cargar_inventario(sucursal_id)
        
        # Posicionarse en la entrada
        entrada = self.mapa_sucursal['entrada']
        self.posicion_actual = (entrada['fila'], entrada['columna'])
        
        self.estado = "en_sucursal"
        
        print(f"  ✓ Ingreso exitoso a {self.mapa_sucursal['nombre']}")
        print(f"  ✓ Posición inicial: {self.posicion_actual}")
    
    def _obtener_posicion_producto(self, producto_id: int) -> Optional[Tuple[int, int]]:
        """
        Obtiene la posición de un producto en el mapa.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Tupla (fila, columna) o None si no se encuentra
        """
        zonas_productos = self.mapa_sucursal.get('zonas_productos', {})
        
        for zona, info in zonas_productos.items():
            if producto_id in info.get('productos', []):
                return (info['fila'], info['columna'])
        
        return None
    
    def _obtener_producto_por_id(self, producto_id: int) -> Optional[Dict]:
        """
        Obtiene la información de un producto del inventario.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Diccionario con información del producto o None
        """
        productos = self.inventario_sucursal.get('productos', [])
        for producto in productos:
            if producto['id'] == producto_id:
                return producto
        return None
    
    def planificar_compra(self, lista_compras: List[Dict]):
        """
        Planifica la ruta óptima para recolectar todos los productos.
        
        Args:
            lista_compras: Lista de productos a comprar
                          [{'id': 1, 'nombre': '...', 'cantidad': 2}, ...]
        """
        if self.estado != "en_sucursal":
            raise ValueError("El comprador debe estar en la sucursal para planificar")
        
        print(f"\n[Agente Comprador {self.comprador_id}] Planificando compra...")
        print(f"  Productos solicitados: {len(lista_compras)}")
        
        self.lista_compras = lista_compras
        self.estado = "comprando"
        
        # Obtener posiciones de todos los productos
        posiciones_productos = []
        productos_info = []
        
        for item in lista_compras:
            producto_id = item['id']
            posicion = self._obtener_posicion_producto(producto_id)
            
            if posicion:
                # Evitar duplicados de posiciones
                if posicion not in posiciones_productos:
                    posiciones_productos.append(posicion)
                    productos_info.append({
                        'producto_id': producto_id,
                        'nombre': item['nombre'],
                        'cantidad': item['cantidad'],
                        'posicion': posicion
                    })
            else:
                print(f"  ⚠️  Producto {item['nombre']} (ID: {producto_id}) no encontrado en el mapa")
        
        print(f"  Zonas a visitar: {len(posiciones_productos)}")
        
        # Planificar ruta usando A* con múltiples objetivos
        if posiciones_productos:
            print("  Calculando ruta óptima con A*...")
            
            try:
                ruta, distancia = self.a_estrella.buscar_ruta_multiple(
                    self.posicion_actual,
                    posiciones_productos,
                    self.mapa_sucursal
                )
                
                self.ruta_completa = ruta
                self.distancia_total = distancia
                
                # Agregar ruta a la caja
                caja = self.mapa_sucursal['caja']
                posicion_caja = (caja['fila'], caja['columna'])
                
                if ruta[-1] != posicion_caja:
                    ruta_a_caja = self.a_estrella.buscar_ruta(
                        ruta[-1],
                        posicion_caja,
                        self.mapa_sucursal
                    )
                    
                    if len(ruta_a_caja) > 1:
                        self.ruta_completa.extend(ruta_a_caja[1:])
                        self.distancia_total += len(ruta_a_caja) - 1
                
                # Registrar productos recolectados
                for info in productos_info:
                    self.productos_recolectados.append(info)
                
                print(f"  ✓ Ruta calculada exitosamente")
                print(f"  ✓ Distancia total: {self.distancia_total} pasos")
                print(f"  ✓ Productos a recolectar: {len(self.productos_recolectados)}")
                
            except ValueError as e:
                print(f"  ✗ Error al calcular ruta: {e}")
                raise
        else:
            print("  ⚠️  No hay productos para recolectar")
    
    def ejecutar_compra(self) -> Dict:
        """
        Ejecuta la compra siguiendo la ruta planificada.
        
        Returns:
            Diccionario con el resultado de la compra
        """
        if self.estado != "comprando":
            raise ValueError("Debe planificar la compra primero")
        
        print(f"\n[Agente Comprador {self.comprador_id}] Ejecutando compra...")
        
        # Generar ruta detallada con acciones
        ruta_detallada = self._generar_ruta_detallada()
        
        # Actualizar posición final
        if self.ruta_completa:
            self.posicion_actual = self.ruta_completa[-1]
        
        self.estado = "finalizado"
        
        # Calcular resumen
        total_items = sum(p['cantidad'] for p in self.productos_recolectados)
        tiempo_estimado = self._estimar_tiempo()
        
        print(f"  ✓ Compra finalizada")
        print(f"  ✓ Items recolectados: {total_items}")
        print(f"  ✓ Tiempo estimado: {tiempo_estimado}")
        
        return {
            'comprador_id': self.comprador_id,
            'sucursal_id': self.sucursal_id,
            'sucursal_nombre': self.mapa_sucursal['nombre'],
            'productos_recolectados': self.productos_recolectados,
            'ruta_detallada': ruta_detallada,
            'distancia_total': self.distancia_total,
            'total_items': total_items,
            'tiempo_estimado': tiempo_estimado,
            'posicion_final': self.posicion_actual,
            'estado': self.estado
        }
    
    def _generar_ruta_detallada(self) -> List[Dict]:
        """
        Genera una ruta detallada con acciones en cada paso.
        
        Returns:
            Lista de diccionarios con información de cada paso
        """
        ruta_detallada = []
        productos_visitados = set()
        
        for i, posicion in enumerate(self.ruta_completa):
            paso = {
                'paso': i + 1,
                'posicion': list(posicion),
                'accion': 'avanzar'
            }
            
            # Determinar si es un punto especial
            entrada = self.mapa_sucursal['entrada']
            caja = self.mapa_sucursal['caja']
            
            if posicion == (entrada['fila'], entrada['columna']) and i == 0:
                paso['accion'] = 'inicio'
                paso['descripcion'] = 'Entrada al supermercado'
            elif posicion == (caja['fila'], caja['columna']):
                paso['accion'] = 'caja'
                paso['descripcion'] = 'Llegar a la caja'
            else:
                # Verificar si es una zona de producto
                for producto_info in self.productos_recolectados:
                    if posicion == producto_info['posicion'] and posicion not in productos_visitados:
                        paso['accion'] = 'recoger_producto'
                        paso['producto'] = {
                            'id': producto_info['producto_id'],
                            'nombre': producto_info['nombre'],
                            'cantidad': producto_info['cantidad']
                        }
                        paso['descripcion'] = f"Recoger {producto_info['cantidad']}x {producto_info['nombre']}"
                        productos_visitados.add(posicion)
                        break
            
            ruta_detallada.append(paso)
        
        return ruta_detallada
    
    def _estimar_tiempo(self) -> str:
        """
        Estima el tiempo que tomará completar la compra.
        
        Returns:
            Tiempo estimado en formato legible
        """
        # Estimación: 2 segundos por paso + 10 segundos por producto
        tiempo_movimiento = self.distancia_total * 2
        tiempo_recoleccion = len(self.productos_recolectados) * 10
        tiempo_total_segundos = tiempo_movimiento + tiempo_recoleccion
        
        minutos = tiempo_total_segundos // 60
        segundos = tiempo_total_segundos % 60
        
        if minutos > 0:
            return f"{int(minutos)} min {int(segundos)} seg"
        else:
            return f"{int(segundos)} seg"
    
    def obtener_estado(self) -> Dict:
        """
        Retorna el estado actual del agente comprador.
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'comprador_id': self.comprador_id,
            'estado': self.estado,
            'sucursal_id': self.sucursal_id,
            'sucursal_nombre': self.mapa_sucursal['nombre'] if self.mapa_sucursal else None,
            'posicion_actual': self.posicion_actual,
            'productos_en_lista': len(self.lista_compras) if self.lista_compras else 0,
            'productos_recolectados': len(self.productos_recolectados),
            'distancia_recorrida': self.distancia_total
        }
    
    def reiniciar(self):
        """Reinicia el estado del agente para una nueva compra."""
        self.sucursal_id = None
        self.mapa_sucursal = None
        self.inventario_sucursal = None
        self.posicion_actual = None
        self.lista_compras = None
        self.productos_recolectados = []
        self.ruta_completa = []
        self.distancia_total = 0
        self.estado = "disponible"
        
        print(f"[Agente Comprador {self.comprador_id}] Reiniciado y disponible")
