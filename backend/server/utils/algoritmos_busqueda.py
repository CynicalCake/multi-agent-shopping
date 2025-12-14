"""
Algoritmos de Búsqueda y Optimización
Este módulo contiene las implementaciones de los algoritmos de IA utilizados por los agentes.
"""

import random
import math
from typing import List, Dict, Tuple, Set


class TempleSimulado:
    """
    Implementación del algoritmo de Temple Simulado para optimización
    de listas de compras basado en presupuesto y preferencias.
    """
    
    def __init__(
        self,
        temperatura_inicial: float = 1000.0,
        temperatura_minima: float = 1.0,
        factor_enfriamiento: float = 0.95,
        iteraciones_por_temperatura: int = 100
    ):
        """
        Inicializa el algoritmo de Temple Simulado.
        
        Args:
            temperatura_inicial: Temperatura de inicio del algoritmo
            temperatura_minima: Temperatura mínima antes de detener
            factor_enfriamiento: Factor de reducción de temperatura (0-1)
            iteraciones_por_temperatura: Iteraciones antes de enfriar
        """
        self.temperatura_inicial = temperatura_inicial
        self.temperatura_minima = temperatura_minima
        self.factor_enfriamiento = factor_enfriamiento
        self.iteraciones_por_temperatura = iteraciones_por_temperatura
    
    def calcular_costo(
        self,
        lista_compras: List[Tuple[Dict, int]],
        presupuesto: float,
        categorias_preferidas: List[str],
        inventario: List[Dict]
    ) -> float:
        """
        Calcula el costo (valor a minimizar) de una lista de compras.
        
        Args:
            lista_compras: Lista de tuplas (producto, cantidad)
            presupuesto: Presupuesto objetivo
            categorias_preferidas: Categorías que el usuario prefiere
            inventario: Inventario completo de productos
            
        Returns:
            Valor de costo (menor es mejor)
        """
        if not lista_compras:
            return float('inf')
        
        # Calcular total de la compra
        total = sum(producto['precio'] * cantidad for producto, cantidad in lista_compras)
        
        # 1. Penalización por diferencia de presupuesto (peso alto)
        diferencia_presupuesto = abs(total - presupuesto)
        penalizacion_presupuesto = diferencia_presupuesto ** 2
        
        # 2. Penalización por falta de realismo
        penalizacion_realismo = 0.0
        productos_ids = {}
        for producto, cantidad in lista_compras:
            prod_id = producto['id']
            if prod_id in productos_ids:
                # Producto repetido, verificar si excede cantidad típica
                productos_ids[prod_id] += cantidad
            else:
                productos_ids[prod_id] = cantidad
            
            # Penalizar cantidades muy alejadas de la típica
            cantidad_tipica = producto.get('cantidad_tipica', 1)
            if cantidad > cantidad_tipica * 3:  # Más de 3x la cantidad típica
                penalizacion_realismo += (cantidad - cantidad_tipica * 3) * 10
        
        # 3. Penalización por baja importancia de productos
        importancia_total = sum(
            producto.get('importancia', 0.5) * cantidad 
            for producto, cantidad in lista_compras
        )
        num_items = sum(cantidad for _, cantidad in lista_compras)
        importancia_promedio = importancia_total / num_items if num_items > 0 else 0
        penalizacion_importancia = (1.0 - importancia_promedio) * 50
        
        # 4. Penalización por falta de variedad
        num_productos_diferentes = len(productos_ids)
        if num_productos_diferentes < 3:
            penalizacion_variedad = (3 - num_productos_diferentes) * 30
        else:
            penalizacion_variedad = 0
        
        # 5. Bonificación por cumplir categorías preferidas
        penalizacion_categoria = 0.0
        if categorias_preferidas:
            categorias_en_lista = set(p['categoria'] for p, _ in lista_compras)
            categorias_faltantes = set(categorias_preferidas) - categorias_en_lista
            penalizacion_categoria = len(categorias_faltantes) * 25
        
        # Costo total ponderado
        costo_total = (
            penalizacion_presupuesto * 1.0 +
            penalizacion_realismo * 0.5 +
            penalizacion_importancia * 0.3 +
            penalizacion_variedad * 0.4 +
            penalizacion_categoria * 0.6
        )
        
        return costo_total
    
    def generar_vecino(
        self,
        lista_actual: List[Tuple[Dict, int]],
        inventario: List[Dict],
        presupuesto: float
    ) -> List[Tuple[Dict, int]]:
        """
        Genera un vecino (solución cercana) de la lista actual.
        
        Args:
            lista_actual: Lista de compras actual
            inventario: Inventario de productos disponibles
            presupuesto: Presupuesto objetivo
            
        Returns:
            Nueva lista de compras (vecino)
        """
        nueva_lista = lista_actual.copy()
        accion = random.choice(['agregar', 'quitar', 'modificar', 'reemplazar'])
        
        if accion == 'agregar' or not nueva_lista:
            # Agregar un producto aleatorio
            producto = random.choice(inventario)
            cantidad = random.randint(1, producto.get('cantidad_tipica', 1) * 2)
            nueva_lista.append((producto, cantidad))
            
        elif accion == 'quitar' and len(nueva_lista) > 1:
            # Quitar un producto aleatorio
            indice = random.randint(0, len(nueva_lista) - 1)
            nueva_lista.pop(indice)
            
        elif accion == 'modificar' and nueva_lista:
            # Modificar cantidad de un producto
            indice = random.randint(0, len(nueva_lista) - 1)
            producto, cantidad_actual = nueva_lista[indice]
            nueva_cantidad = max(1, cantidad_actual + random.randint(-2, 2))
            nueva_lista[indice] = (producto, nueva_cantidad)
            
        elif accion == 'reemplazar' and nueva_lista:
            # Reemplazar un producto por otro
            indice = random.randint(0, len(nueva_lista) - 1)
            _, cantidad = nueva_lista[indice]
            nuevo_producto = random.choice(inventario)
            nueva_lista[indice] = (nuevo_producto, cantidad)
        
        return nueva_lista
    
    def optimizar(
        self,
        inventario: List[Dict],
        presupuesto: float,
        categorias_preferidas: List[str] = None
    ) -> List[Tuple[Dict, int]]:
        """
        Ejecuta el algoritmo de Temple Simulado para encontrar una lista óptima.
        
        Args:
            inventario: Lista de productos disponibles
            presupuesto: Presupuesto objetivo
            categorias_preferidas: Categorías preferidas por el usuario
            
        Returns:
            Lista de compras optimizada [(producto, cantidad), ...]
        """
        if categorias_preferidas is None:
            categorias_preferidas = []
        
        # Estado inicial: lista vacía o con algunos productos básicos
        estado_actual = []
        
        # Agregar algunos productos iniciales de alta importancia
        productos_importantes = sorted(
            inventario, 
            key=lambda p: p.get('importancia', 0), 
            reverse=True
        )[:5]
        
        for producto in productos_importantes:
            if random.random() > 0.5:  # 50% de probabilidad
                cantidad = random.randint(1, producto.get('cantidad_tipica', 1))
                estado_actual.append((producto, cantidad))
        
        costo_actual = self.calcular_costo(
            estado_actual, presupuesto, categorias_preferidas, inventario
        )
        
        mejor_estado = estado_actual.copy()
        mejor_costo = costo_actual
        
        temperatura = self.temperatura_inicial
        
        # Proceso de temple simulado
        while temperatura > self.temperatura_minima:
            for _ in range(self.iteraciones_por_temperatura):
                # Generar vecino
                estado_vecino = self.generar_vecino(estado_actual, inventario, presupuesto)
                costo_vecino = self.calcular_costo(
                    estado_vecino, presupuesto, categorias_preferidas, inventario
                )
                
                # Calcular diferencia de costos
                delta_costo = costo_vecino - costo_actual
                
                # Decidir si aceptar el vecino
                if delta_costo < 0:
                    # Mejor solución, aceptar siempre
                    estado_actual = estado_vecino
                    costo_actual = costo_vecino
                    
                    # Actualizar mejor solución global
                    if costo_actual < mejor_costo:
                        mejor_estado = estado_actual.copy()
                        mejor_costo = costo_actual
                else:
                    # Peor solución, aceptar con probabilidad
                    probabilidad = math.exp(-delta_costo / temperatura)
                    if random.random() < probabilidad:
                        estado_actual = estado_vecino
                        costo_actual = costo_vecino
            
            # Enfriar temperatura
            temperatura *= self.factor_enfriamiento
        
        return mejor_estado


class BusquedaAEstrella:
    """
    Implementación del algoritmo A* para búsqueda de rutas óptimas.
    Utiliza la distancia Manhattan como heurística.
    """
    
    def __init__(self):
        """Inicializa el algoritmo A*."""
        self.movimientos = [
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1),   # Derecha
        ]
    
    def heuristica_manhattan(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calcula la distancia Manhattan entre dos posiciones.
        
        Args:
            pos1: Primera posición (fila, columna)
            pos2: Segunda posición (fila, columna)
            
        Returns:
            Distancia Manhattan
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def es_posicion_valida(
        self, 
        posicion: Tuple[int, int], 
        obstaculos: Set[Tuple[int, int]],
        dimensiones: Tuple[int, int]
    ) -> bool:
        """
        Verifica si una posición es válida (dentro del mapa y sin obstáculos).
        
        Args:
            posicion: Posición a verificar (fila, columna)
            obstaculos: Set de posiciones con obstáculos
            dimensiones: Dimensiones del mapa (filas, columnas)
            
        Returns:
            True si la posición es válida, False en caso contrario
        """
        fila, columna = posicion
        filas, columnas = dimensiones
        
        # Verificar límites del mapa
        if fila < 0 or fila >= filas or columna < 0 or columna >= columnas:
            return False
        
        # Verificar obstáculos
        if posicion in obstaculos:
            return False
        
        return True
    
    def reconstruir_ruta(
        self, 
        padre: Dict[Tuple[int, int], Tuple[int, int]], 
        inicio: Tuple[int, int], 
        objetivo: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Reconstruye la ruta desde el inicio hasta el objetivo.
        
        Args:
            padre: Diccionario de padres de cada nodo
            inicio: Posición inicial
            objetivo: Posición objetivo
            
        Returns:
            Lista de posiciones que forman la ruta
        """
        ruta = []
        actual = objetivo
        
        while actual != inicio:
            ruta.append(actual)
            actual = padre[actual]
        
        ruta.append(inicio)
        ruta.reverse()
        
        return ruta
    
    def buscar_ruta(
        self, 
        inicio: Tuple[int, int], 
        objetivo: Tuple[int, int], 
        mapa: Dict
    ) -> List[Tuple[int, int]]:
        """
        Encuentra la ruta óptima entre dos puntos usando A*.
        
        Args:
            inicio: Posición inicial (fila, columna)
            objetivo: Posición objetivo (fila, columna)
            mapa: Diccionario con la información del mapa
            
        Returns:
            Lista de posiciones que forman la ruta óptima
        """
        # Extraer información del mapa
        dimensiones = (mapa['dimensiones']['filas'], mapa['dimensiones']['columnas'])
        obstaculos = set(
            (obst['fila'], obst['columna']) 
            for obst in mapa.get('obstaculos', [])
        )
        
        # Verificar que inicio y objetivo sean válidos
        if not self.es_posicion_valida(inicio, obstaculos, dimensiones):
            raise ValueError(f"Posición de inicio inválida: {inicio}")
        if not self.es_posicion_valida(objetivo, obstaculos, dimensiones):
            raise ValueError(f"Posición de objetivo inválida: {objetivo}")
        
        # Si inicio y objetivo son iguales, retornar
        if inicio == objetivo:
            return [inicio]
        
        # Inicializar estructuras de datos
        import heapq
        
        # Cola de prioridad: (f_score, contador, posición)
        contador = 0
        frontera = [(0, contador, inicio)]
        heapq.heapify(frontera)
        
        # Diccionario de padres
        padre = {}
        
        # g_score: costo desde el inicio hasta cada nodo
        g_score = {inicio: 0}
        
        # f_score: g_score + heurística
        f_score = {inicio: self.heuristica_manhattan(inicio, objetivo)}
        
        # Set de nodos visitados
        visitados = set()
        
        # Proceso de búsqueda A*
        while frontera:
            # Obtener nodo con menor f_score
            _, _, actual = heapq.heappop(frontera)
            
            # Si llegamos al objetivo, reconstruir ruta
            if actual == objetivo:
                return self.reconstruir_ruta(padre, inicio, objetivo)
            
            # Marcar como visitado
            if actual in visitados:
                continue
            visitados.add(actual)
            
            # Explorar vecinos
            for movimiento in self.movimientos:
                vecino = (actual[0] + movimiento[0], actual[1] + movimiento[1])
                
                # Verificar si el vecino es válido
                if not self.es_posicion_valida(vecino, obstaculos, dimensiones):
                    continue
                
                # Calcular nuevo g_score
                nuevo_g_score = g_score[actual] + 1
                
                # Si encontramos un mejor camino al vecino
                if vecino not in g_score or nuevo_g_score < g_score[vecino]:
                    # Actualizar información del vecino
                    padre[vecino] = actual
                    g_score[vecino] = nuevo_g_score
                    f_score[vecino] = nuevo_g_score + self.heuristica_manhattan(vecino, objetivo)
                    
                    # Agregar a la frontera
                    contador += 1
                    heapq.heappush(frontera, (f_score[vecino], contador, vecino))
        
        # No se encontró ruta
        raise ValueError(f"No existe ruta desde {inicio} hasta {objetivo}")
    
    def buscar_ruta_multiple(
        self, 
        inicio: Tuple[int, int],
        objetivos: List[Tuple[int, int]], 
        mapa: Dict
    ) -> Tuple[List[Tuple[int, int]], float]:
        """
        Encuentra una ruta que visite múltiples objetivos.
        Utiliza una heurística del vecino más cercano.
        
        Args:
            inicio: Posición inicial
            objetivos: Lista de posiciones objetivo a visitar
            mapa: Diccionario con la información del mapa
            
        Returns:
            Tupla (ruta_completa, distancia_total)
        """
        if not objetivos:
            return [inicio], 0.0
        
        ruta_completa = [inicio]
        distancia_total = 0.0
        posicion_actual = inicio
        objetivos_restantes = objetivos.copy()
        
        # Estrategia: Visitar el objetivo más cercano primero
        while objetivos_restantes:
            # Encontrar el objetivo más cercano
            objetivo_mas_cercano = min(
                objetivos_restantes,
                key=lambda obj: self.heuristica_manhattan(posicion_actual, obj)
            )
            
            # Buscar ruta al objetivo más cercano
            try:
                ruta_parcial = self.buscar_ruta(posicion_actual, objetivo_mas_cercano, mapa)
                
                # Agregar ruta (sin duplicar el punto actual)
                if len(ruta_parcial) > 1:
                    ruta_completa.extend(ruta_parcial[1:])
                    distancia_total += len(ruta_parcial) - 1
                
                # Actualizar posición actual
                posicion_actual = objetivo_mas_cercano
                objetivos_restantes.remove(objetivo_mas_cercano)
                
            except ValueError as e:
                print(f"[A*] Advertencia: No se puede llegar a {objetivo_mas_cercano}: {e}")
                objetivos_restantes.remove(objetivo_mas_cercano)
        
        return ruta_completa, distancia_total
