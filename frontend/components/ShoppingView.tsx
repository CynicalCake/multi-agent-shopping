"use client"

import { useEffect, useState, useRef } from "react"
import { motion } from "framer-motion"
import { MapPin, Package, Navigation, CheckCircle2 } from "lucide-react"
import { api, type MapData, type ShoppingResult, type RouteStep } from "@/lib/api"

interface Props {
  compradorId: string
  sucursalId: string
  mapData: MapData
  selectedProducts: Array<{ id: number; nombre: string; cantidad: number }>
  onComplete: (result: ShoppingResult) => void
}

// Flag global para evitar múltiples ejecuciones desde diferentes instancias del componente
const shoppingStartedMap = new Map<string, boolean>()

export default function ShoppingView({ compradorId, sucursalId, mapData, selectedProducts, onComplete }: Props) {
  const [currentStep, setCurrentStep] = useState(0)
  const [route, setRoute] = useState<RouteStep[]>([])
  const [status, setStatus] = useState<"planning" | "shopping" | "complete">("planning")
  const [result, setResult] = useState<ShoppingResult | null>(null)
  const isExecutingRef = useRef(false)
  const animationStartedRef = useRef(false)

  useEffect(() => {
    const shoppingKey = `${compradorId}-${sucursalId}`
    
    // Verificar si ya se inició la compra para este comprador
    if (shoppingStartedMap.get(shoppingKey)) {
      console.log("[ShoppingView] Ya se inició la compra para este comprador, omitiendo")
      return
    }
    
    // Marcar como iniciado INMEDIATAMENTE
    shoppingStartedMap.set(shoppingKey, true)
    isExecutingRef.current = true
    
    const startShopping = async () => {
      try {
        // Start shopping and get planned route
        console.log("[ShoppingView] Iniciando compra...")
        console.log("[ShoppingView] Datos:", { compradorId, sucursalId, selectedProducts })
        
        const planResult = await api.startShopping(compradorId, sucursalId, selectedProducts)
        console.log("[ShoppingView] Planificación completada:", planResult)

        // Get complete shopping result
        console.log("[ShoppingView] Obteniendo resultado completo...")
        const shoppingResult = await api.completeShopping(compradorId)
        
        // Log para diagnosticar
        console.log("[ShoppingView] Backend response:", shoppingResult)
        console.log("[ShoppingView] ruta_detallada:", shoppingResult?.ruta_detallada)
        
        // Validar que ruta_detallada existe y es un array
        const routeData = shoppingResult?.ruta_detallada || []
        if (!Array.isArray(routeData)) {
          console.error("[ShoppingView] ruta_detallada no es un array:", routeData)
          setRoute([])
        } else {
          setRoute(routeData)
        }
        
        setResult(shoppingResult)
      } catch (error) {
        console.error("[ShoppingView] Error starting shopping:", error)
        setStatus("complete")
      }
    }

    startShopping()
    
    // Cleanup: solo resetear el Map, pero no interrumpir la ejecución en curso
    return () => {
      // Si esta instancia NO es la que está ejecutando, podemos limpiar
      if (!isExecutingRef.current) {
        shoppingStartedMap.delete(shoppingKey)
      }
    }
  }, [])

  // Effect separado para iniciar la animación cuando route esté disponible
  useEffect(() => {
    if (route.length > 0 && !animationStartedRef.current && result) {
      console.log("[ShoppingView] Iniciando animación con", route.length, "pasos")
      animationStartedRef.current = true
      
      setTimeout(() => {
        setStatus("shopping")
        animateRoute(route)
      }, 1000)
    } else if (route.length === 0 && result) {
      console.warn("[ShoppingView] No hay ruta para animar")
      setStatus("complete")
    }
  }, [route, result]) // Array vacío: solo ejecutar una vez al montar el componente

  const animateRoute = (routeSteps: RouteStep[]) => {
    // Validar que routeSteps es un array válido
    if (!routeSteps || !Array.isArray(routeSteps) || routeSteps.length === 0) {
      console.error("[ShoppingView] animateRoute: routeSteps inválido", routeSteps)
      setStatus("complete")
      return
    }
    
    let step = 0
    const interval = setInterval(() => {
      step++
      setCurrentStep(step)

      if (step >= routeSteps.length) {
        clearInterval(interval)
        setStatus("complete")
        setTimeout(() => {
          if (result) onComplete(result)
        }, 1500)
      }
    }, 300) // 300ms per step
    
    // Retornar función de limpieza
    return () => clearInterval(interval)
  }

  const getCellClass = (row: number, col: number): string => {
    const position: [number, number] = [row, col]

    // Check if it's the current position
    if (currentStep > 0 && currentStep <= route.length) {
      const currentPos = route[currentStep - 1].posicion
      if (currentPos[0] === row && currentPos[1] === col) {
        return "grid-cell-agent"
      }
    }

    // Check if it's part of the path (already visited)
    if (currentStep > 0) {
      for (let i = 0; i < Math.min(currentStep, route.length); i++) {
        const stepPos = route[i].posicion
        if (stepPos[0] === row && stepPos[1] === col) {
          return "grid-cell-path"
        }
      }
    }

    // Check if it's entrance
    if (row === mapData.entrada.fila && col === mapData.entrada.columna) {
      return "grid-cell-entrance"
    }

    // Check if it's checkout
    if (row === mapData.caja.fila && col === mapData.caja.columna) {
      return "grid-cell-checkout"
    }

    // Check if it's a product zone
    for (const zona of Object.values(mapData.zonas_productos)) {
      if (zona.fila === row && zona.columna === col) {
        return "grid-cell-product"
      }
    }

    // Check if it's an obstacle
    const isObstacle = mapData.obstaculos.some((obs) => obs.fila === row && obs.columna === col)
    if (isObstacle) {
      return "grid-cell-obstacle"
    }

    return "grid-cell-empty"
  }

  const currentRouteStep = currentStep > 0 && currentStep <= route.length ? route[currentStep - 1] : null

  return (
    <div className="grid lg:grid-cols-[1fr_400px] gap-8">
      {/* Map visualization */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-card border border-border rounded-xl p-6"
      >
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-2">Mapa de Navegación</h2>
          <p className="text-muted-foreground">Siguiendo al agente comprador en tiempo real</p>
        </div>

        {/* Grid map */}
        <div className="overflow-auto">
          <div
            className="inline-grid gap-[1px] bg-border p-1 rounded-lg"
            style={{
              gridTemplateColumns: `repeat(${mapData.dimensiones.columnas}, minmax(20px, 1fr))`,
              gridTemplateRows: `repeat(${mapData.dimensiones.filas}, minmax(20px, 1fr))`,
              minWidth: "600px",
            }}
          >
            {Array.from({ length: mapData.dimensiones.filas }).map((_, row) =>
              Array.from({ length: mapData.dimensiones.columnas }).map((_, col) => (
                <div key={`${row}-${col}`} className={`grid-cell ${getCellClass(row, col)}`} />
              )),
            )}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-primary" />
            <span className="text-muted-foreground">Agente</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-primary/20 border border-primary" />
            <span className="text-muted-foreground">Entrada</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-accent/20 border border-accent" />
            <span className="text-muted-foreground">Caja</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-accent/30 border border-accent/60" />
            <span className="text-muted-foreground">Productos</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-secondary border border-border" />
            <span className="text-muted-foreground">Estantes</span>
          </div>
        </div>
      </motion.div>

      {/* Status panel */}
      <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
        {/* Current action */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Estado Actual</h3>

          {status === "planning" && (
            <div className="text-center py-8">
              <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-4">
                <Navigation className="w-6 h-6 text-primary animate-pulse" />
              </div>
              <p className="text-muted-foreground">Planificando ruta...</p>
            </div>
          )}

          {status === "shopping" && currentRouteStep && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-muted-foreground">
                  Paso {currentStep} de {route.length}
                </span>
                <span className="text-sm font-medium text-primary">
                  {Math.round((currentStep / route.length) * 100)}%
                </span>
              </div>

              <div className="mb-4">
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-primary"
                    initial={{ width: 0 }}
                    animate={{ width: `${(currentStep / route.length) * 100}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Posición</p>
                    <p className="text-foreground font-medium">
                      Fila {currentRouteStep.posicion[0]}, Columna {currentRouteStep.posicion[1]}
                    </p>
                  </div>
                </div>

                {currentRouteStep.accion === "recoger_producto" && currentRouteStep.producto && (
                  <div className="flex items-center gap-3 p-3 bg-accent/10 border border-accent/20 rounded-lg">
                    <Package className="w-5 h-5 text-accent" />
                    <div>
                      <p className="text-sm font-medium text-foreground">{currentRouteStep.producto.nombre}</p>
                      <p className="text-xs text-muted-foreground">Cantidad: {currentRouteStep.producto.cantidad}</p>
                    </div>
                  </div>
                )}

                {currentRouteStep.accion === "caja" && (
                  <div className="flex items-center gap-3 p-3 bg-primary/10 border border-primary/20 rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-primary" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Llegando a la caja</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {status === "complete" && (
            <div className="text-center py-8">
              <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-6 h-6 text-primary-foreground" />
              </div>
              <p className="text-foreground font-medium mb-1">Compra completada</p>
              <p className="text-sm text-muted-foreground">Generando informe...</p>
            </div>
          )}
        </div>

        {/* Shopping list */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Lista de Compras</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {selectedProducts.map((product) => {
              // Validar que route existe antes de usar slice
              const collected = route && Array.isArray(route) 
                ? route.slice(0, currentStep).some((step) => step.producto?.id === product.id)
                : false
              return (
                <div
                  key={product.id}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    collected ? "bg-primary/10 border-primary/20" : "bg-muted border-border"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {collected ? (
                      <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-muted-foreground flex-shrink-0" />
                    )}
                    <span className={collected ? "text-foreground font-medium" : "text-muted-foreground"}>
                      {product.nombre}
                    </span>
                  </div>
                  <span className="text-sm text-muted-foreground">x{product.cantidad}</span>
                </div>
              )
            })}
          </div>
        </div>
      </motion.div>
    </div>
  )
}
