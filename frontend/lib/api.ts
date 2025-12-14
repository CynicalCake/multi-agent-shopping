// API utilities for backend communication

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

export interface Sucursal {
  sucursal_id: string
  nombre: string
  productos_disponibles: number
  estado: string
}

export interface Producto {
  id: number
  nombre: string
  precio: number
  categoria: string
  importancia: number
  cantidad_tipica: number
}

export interface RecommendationProduct {
  id: number
  nombre: string
  precio_unitario: number
  cantidad: number
  categoria: string
  subtotal: number
}

export interface Recommendation {
  tipo: "exacta" | "superior" | "inferior"
  total: number
  diferencia: number
  porcentaje_diferencia: number
  productos: RecommendationProduct[]
  cantidad_items: number
  cantidad_productos_diferentes: number
  mensaje: string
}

export interface RecommendationResponse {
  sucursal_id: string
  sucursal_nombre: string
  presupuesto_solicitado: number
  categorias_preferidas: string[]
  recomendaciones: Recommendation[]
}

export interface MapData {
  sucursal_id: string
  nombre: string
  dimensiones: {
    filas: number
    columnas: number
  }
  entrada: {
    fila: number
    columna: number
    tipo: string
  }
  caja: {
    fila: number
    columna: number
    tipo: string
  }
  zonas_productos: {
    [key: string]: {
      fila: number
      columna: number
      productos: number[]
    }
  }
  obstaculos: Array<{
    fila: number
    columna: number
    tipo: string
  }>
}

export interface RouteStep {
  paso: number
  posicion: [number, number]
  accion: string
  producto?: {
    id: number
    nombre: string
    cantidad: number
  }
  descripcion?: string
}

export interface ShoppingResult {
  comprador_id: string
  sucursal_id: string
  sucursal_nombre: string
  productos_recolectados: Array<{
    producto_id: number
    nombre: string
    cantidad: number
    posicion: [number, number]
  }>
  ruta_detallada: RouteStep[]
  distancia_total: number
  total_items: number
  tiempo_estimado: string
  posicion_final: [number, number]
  estado: string
}

export const api = {
  // Get all sucursales
  getSucursales: async (): Promise<{ sucursales: Sucursal[] }> => {
    const response = await fetch(`${API_URL}/api/sucursales`)
    return response.json()
  },

  // Get map for sucursal
  getMap: async (sucursalId: string): Promise<MapData> => {
    const response = await fetch(`${API_URL}/api/sucursal/${sucursalId}/mapa`)
    return response.json()
  },

  // Get inventory for sucursal
  getInventory: async (sucursalId: string): Promise<{ productos: Producto[] }> => {
    const response = await fetch(`${API_URL}/api/sucursal/${sucursalId}/inventario`)
    return response.json()
  },

  // Request recommendations
  getRecommendations: async (
    sucursalId: string,
    presupuesto: number,
    categorias?: string[],
  ): Promise<RecommendationResponse> => {
    const response = await fetch(`${API_URL}/api/recomendador/solicitar`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sucursal_id: sucursalId,
        presupuesto,
        categorias_preferidas: categorias || [],
      }),
    })
    return response.json()
  },

  // Create buyer agent
  createBuyer: async (sucursalId: string): Promise<{ comprador_id: string }> => {
    const response = await fetch(`${API_URL}/api/comprador/crear`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sucursal_id: sucursalId,
      }),
    })
    return response.json()
  },

  // Start shopping
  startShopping: async (
    compradorId: string,
    sucursalId: string,
    listaCompras: Array<{ id: number; nombre: string; cantidad: number }>,
  ): Promise<any> => {
    console.log("[API] Iniciando compra:", { compradorId, sucursalId, listaCompras })
    
    const response = await fetch(`${API_URL}/api/comprador/iniciar_compra`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        comprador_id: compradorId,
        sucursal_id: sucursalId,
        lista_compras: listaCompras,
      }),
    })
    
    const data = await response.json()
    console.log("[API] Respuesta de iniciar_compra:", data)
    
    if (!response.ok) {
      console.error("[API] Error en startShopping:", data)
      throw new Error(data.detalle || data.error || "Error al iniciar compra")
    }
    
    return data
  },

  // Complete shopping
  completeShopping: async (compradorId: string): Promise<ShoppingResult> => {
    const response = await fetch(`${API_URL}/api/comprador/compra_completa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        comprador_id: compradorId,
      }),
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      console.error("[API] Error en completeShopping:", data)
      throw new Error(data.detalle || data.error || "Error al completar compra")
    }
    
    return data
  },
}
