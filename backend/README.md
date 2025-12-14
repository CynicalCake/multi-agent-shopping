# Sistema Multi-Agente de Supermercado 🛒🤖

Sistema inteligente de recomendación y navegación para supermercados utilizando agentes autónomos con técnicas de Inteligencia Artificial.

## 📋 Descripción

Proyecto de Inteligencia Artificial que implementa un sistema multi-agente para:
- **Agente Recomendador**: Genera listas de compras optimizadas usando Temple Simulado ✅
- **Agente Comprador**: Navega eficientemente por la sucursal usando A* ✅

## ⚙️ Fases del Proyecto

### ✅ Fase 1: Agente Recomendador (Completada)
- Temple Simulado para generación de listas de compras
- 3 tipos de recomendaciones (exacta, superior, inferior)
- API REST + WebSockets
- Tests completos

### ✅ Fase 2: Agente Comprador (Completada)
- Algoritmo A* para navegación óptima
- Mapas de sucursales con obstáculos y zonas de productos
- Planificación de rutas multi-destino
- Integración con agente recomendador
- Tests completos

## 🏗️ Arquitectura

```
Propuesta v4/
├── server/                      # Servidor Flask
│   ├── app.py                   # Aplicación principal
│   ├── models/                  # Modelos de agentes
│   │   ├── agente_recomendador.py
│   │   └── agente_comprador.py
│   ├── routes/                  # Rutas de API
│   ├── utils/                   # Algoritmos de IA
│   │   └── algoritmos_busqueda.py
│   └── data/                    # Datos de sucursales
│       ├── inventario/
│       │   ├── SUC001.json
│       │   └── SUC002.json
│       └── mapas/
│           ├── SUC001.json
│           └── SUC002.json
├── test_agente_recomendador.py  # Tests del recomendador
└── README.md
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
cd "Propuesta v4"
```

### 2. Instalar dependencias
```bash
pip install -r server/requirements.txt
```

### 3. Ejecutar pruebas del agente recomendador
```bash
python test_agente_recomendador.py
```

### 4. Iniciar el servidor
```bash
cd server
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 🧪 Pruebas

### Ejecutar pruebas del Agente Recomendador
```bash
python test_agente_recomendador.py
```

Este script ejecutará 5 tests que validan:
- Recomendación básica sin categorías
- Recomendación con categorías preferidas
- Presupuestos bajos (50 Bs.)
- Presupuestos altos (500 Bs.)
- Consulta de estado e inventario

### Ejecutar pruebas del Agente Comprador
```bash
python test_agente_comprador.py
```

Este script ejecutará 7 tests que validan:
- Ingreso a sucursal
- Planificación de compra simple
- Ejecución completa de compra
- Integración con agente recomendador
- Optimización de zonas (múltiples productos en misma área)
- Compras grandes (presupuesto alto)
- Visualización de rutas

## 📡 API Endpoints

### REST API

#### `GET /`
Información general del sistema

#### `GET /api/sucursales`
Lista todas las sucursales disponibles

#### `GET /api/sucursal/<sucursal_id>/inventario`
Obtiene el inventario de una sucursal

#### `GET /api/recomendador/estado/<sucursal_id>`
Estado del agente recomendador

#### `POST /api/recomendador/solicitar`
Solicita recomendaciones de compra

**Body JSON:**
```json
{
  "sucursal_id": "SUC001",
  "presupuesto": 100.0,
  "categorias_preferidas": ["lacteos", "panaderia"]
}
```

**Respuesta:**
```json
{
  "sucursal_id": "SUC001",
  "sucursal_nombre": "Supermercado Central",
  "presupuesto_solicitado": 100.0,
  "categorias_preferidas": ["lacteos", "panaderia"],
  "recomendaciones": [
    {
      "tipo": "exacta",
      "total": 100.0,
      "diferencia": 0.0,
      "productos": [...],
      "mensaje": "Lista ajustada a tu presupuesto"
    },
    {
      "tipo": "superior",
      "total": 103.5,
      "diferencia": 3.5,
      "productos": [...],
      "mensaje": "Te faltan 3.50 Bs. para completar esta compra"
    },
    {
      "tipo": "inferior",
      "total": 97.0,
      "diferencia": -3.0,
      "productos": [...],
      "mensaje": "Con esta lista te sobrarán 3.00 Bs."
    }
  ]
}
```

### Agente Comprador (Fase 2)

#### `GET /api/sucursal/<sucursal_id>/mapa`
Obtiene el mapa de una sucursal con zonas de productos

#### `POST /api/comprador/crear`
Crea un nuevo agente comprador

**Body JSON:**
```json
{
  "sucursal_id": "SUC001"
}
```

#### `POST /api/comprador/iniciar_compra`
Planifica la ruta de compra con A*

**Body JSON:**
```json
{
  "comprador_id": "COMP001",
  "lista_compras": [
    {"id": 1, "nombre": "Leche Entera 1L", "cantidad": 2},
    {"id": 3, "nombre": "Arroz Blanco 1kg", "cantidad": 1}
  ]
}
```

#### `POST /api/comprador/compra_completa`
Ejecuta la compra y retorna la ruta detallada

**Body JSON:**
```json
{
  "comprador_id": "COMP001"
}
```

**Respuesta:**
```json
{
  "comprador_id": "COMP001",
  "sucursal_id": "SUC001",
  "sucursal_nombre": "Supermercado Central",
  "estado": "finalizado",
  "total_items": 3,
  "distancia_total": 45,
  "tiempo_estimado": "2 minutos 15 segundos",
  "productos_recolectados": [...],
  "ruta_detallada": [
    {"paso": 1, "posicion": [0, 15], "accion": "inicio"},
    {"paso": 2, "posicion": [1, 15], "accion": "avanzar"},
    {"paso": 15, "posicion": [5, 8], "accion": "recoger_producto", "producto": {...}},
    ...
    {"paso": 45, "posicion": [19, 15], "accion": "caja"}
  ]
}
```

#### `POST /api/comprador/flujo_completo`
Integración completa: Recomendación + Navegación

**Body JSON:**
```json
{
  "sucursal_id": "SUC001",
  "presupuesto": 150.0,
  "categorias_preferidas": ["lacteos", "verduras"]
}
```

**Respuesta:** Incluye tanto las recomendaciones como la ruta de compra detallada.

### WebSocket Events

#### `connect`
Conexión al sistema

#### `solicitar_recomendacion_ws`
Solicitud de recomendación en tiempo real

**Emitir:**
```json
{
  "sucursal_id": "SUC001",
  "presupuesto": 100.0,
  "categorias_preferidas": ["lacteos"]
}
```

**Escuchar:** `recomendaciones_generadas`

## 🤖 Agentes Inteligentes

### Agente Recomendador

#### Algoritmo: Temple Simulado

El agente utiliza Temple Simulado para optimizar listas de compras considerando:

1. **Presupuesto**: Ajuste preciso al monto disponible
2. **Realismo**: Cantidades típicas de compra
3. **Importancia**: Productos básicos priorizados
4. **Variedad**: Diversidad de productos
5. **Categorías**: Preferencias del usuario

#### Función de Costo

```python
Costo = w1 * diferencia_presupuesto² + 
        w2 * penalización_realismo + 
        w3 * penalización_importancia +
        w4 * penalización_variedad +
        w5 * penalización_categoría
```

#### Parámetros del Temple Simulado

- **Temperatura inicial**: 1000.0
- **Temperatura mínima**: 1.0
- **Factor de enfriamiento**: 0.95
- **Iteraciones por temperatura**: 100

### Agente Comprador

#### Algoritmo: A* (A Estrella)

El agente utiliza A* para navegar eficientemente por la sucursal:

1. **Heurística Manhattan**: Estimación de distancia hasta el objetivo
2. **Evita obstáculos**: Detecta estantes y pasillos bloqueados
3. **Rutas multi-destino**: Visita múltiples productos usando estrategia nearest-neighbor
4. **Optimización de zonas**: Agrupa productos en la misma zona para reducir recorrido

#### Características del A*

- **Función de costo**: `f(n) = g(n) + h(n)`
  - `g(n)`: Costo real desde el inicio hasta el nodo n
  - `h(n)`: Heurística Manhattan: `|x1 - x2| + |y1 - y2|`
- **Cola de prioridad**: Explora primero los nodos con menor f(n)
- **Movimientos**: 4 direcciones (arriba, abajo, izquierda, derecha)
- **Tiempo estimado**: 3 segundos por paso

#### Estructura del Mapa

```json
{
  "sucursal_id": "SUC001",
  "dimensiones": {"filas": 20, "columnas": 30},
  "entrada": [0, 15],
  "caja": [19, 15],
  "zonas_productos": {
    "1": [5, 8],
    "2": [5, 10],
    "3": [5, 12]
  },
  "obstaculos": [[2, 5], [2, 6], ...],
  "pasillos": [[0, 15], [1, 15], ...]
}
```

## 📊 Estructura de Datos

### Producto
```json
{
  "id": 1,
  "nombre": "Leche Entera 1L",
  "precio": 8.5,
  "categoria": "lacteos",
  "importancia": 0.9,
  "cantidad_tipica": 2
}
```

### Inventario
```json
{
  "sucursal_id": "SUC001",
  "nombre": "Supermercado Central",
  "productos": [...]
}
```

## 🏪 Sucursales Disponibles

### SUC001 - Supermercado Central
- **Productos**: 35
- **Mapa**: 20x30 (600 celdas)
- **Zonas de productos**: 15
- **Obstáculos**: 128

### SUC002 - Supermercado Norte
- **Productos**: 38
- **Mapa**: 22x32 (704 celdas)
- **Zonas de productos**: 15
- **Obstáculos**: 144

## 🔧 Tecnologías

- **Python 3.8+**
- **Flask 3.0.0**: Servidor web
- **Flask-SocketIO 5.3.5**: WebSockets para agentes reactivos
- **Flask-CORS 4.0.0**: CORS para frontend

## 📈 Roadmap

### ✅ Fase 1: Agente Recomendador (COMPLETADO)
- [x] Implementación de Temple Simulado
- [x] Sistema de importancia de productos
- [x] Generación de 3 tipos de recomendaciones
- [x] Servidor Flask con REST API
- [x] WebSockets para comunicación en tiempo real
- [x] Tests completos (5 tests)

### ✅ Fase 2: Agente Comprador (COMPLETADO)
- [x] Implementación de A* con heurística Manhattan
- [x] Mapas de sucursales (2 mapas completos)
- [x] Planificación de rutas multi-destino
- [x] Integración con recomendador
- [x] Endpoints de API completos
- [x] Tests completos (7 tests)

### 🚧 Fase 3: Optimizaciones y Mejoras (FUTURO)
- [ ] Algoritmo A* con rutas más inteligentes (TSP)
- [ ] Visualización de mapas en tiempo real
- [ ] Sistema de inventario dinámico
- [ ] Notificaciones push

### 🚧 Fase 4: Frontend (FUTURO)
- [ ] Visualización de mapas interactiva
- [ ] Animaciones de rutas del comprador
- [ ] Dashboard de agentes en tiempo real
- [ ] Interfaz de usuario completa

## 👥 Autores

Proyecto de Inteligencia Artificial - Universidad

## 📄 Licencia

Proyecto académico - 2025
