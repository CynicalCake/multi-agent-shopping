"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import { Bot, DollarSign, ShoppingBag, Check, ChevronRight } from "lucide-react"
import type { RecommendationResponse, Recommendation } from "@/lib/api"

interface Props {
  sucursalId: string
  onBudgetSubmit: (presupuesto: number) => void
  recommendations: RecommendationResponse | null
  onProductSelection: (products: Array<{ id: number; nombre: string; cantidad: number }>) => void
}

export default function RecommenderView({ sucursalId, onBudgetSubmit, recommendations, onProductSelection }: Props) {
  const [presupuesto, setPresupuesto] = useState("")
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const budget = Number.parseFloat(presupuesto)
    if (budget > 0) {
      setLoading(true)
      await onBudgetSubmit(budget)
      setLoading(false)
    }
  }

  const handleSelectRecommendation = () => {
    if (selectedRecommendation) {
      const products = selectedRecommendation.productos.map((p) => ({
        id: p.id,
        nombre: p.nombre,
        cantidad: p.cantidad,
      }))
      onProductSelection(products)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-6xl mx-auto"
    >
      {/* Agent header */}
      <div className="mb-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 border border-primary/20 mb-4">
          <Bot className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Agente Recomendador</h2>
        <p className="text-lg text-muted-foreground text-balance">
          Ingresa tu presupuesto y obtén recomendaciones inteligentes
        </p>
      </div>

      {/* Budget input */}
      {!recommendations && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md mx-auto"
        >
          <form onSubmit={handleSubmit} className="bg-card border border-border rounded-xl p-8">
            <label className="block mb-2 text-sm font-medium text-foreground">Presupuesto disponible</label>
            <div className="relative">
              <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="number"
                step="0.01"
                min="0"
                value={presupuesto}
                onChange={(e) => setPresupuesto(e.target.value)}
                placeholder="100.00"
                className="w-full pl-12 pr-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {loading ? "Generando recomendaciones..." : "Obtener recomendaciones"}
            </button>
          </form>
        </motion.div>
      )}

      {/* Recommendations */}
      {recommendations && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          <div className="text-center mb-8">
            <p className="text-lg text-muted-foreground">
              Presupuesto solicitado:{" "}
              <span className="text-primary font-semibold">{recommendations.presupuesto_solicitado} Bs.</span>
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {recommendations.recomendaciones.map((rec, index) => (
              <motion.div
                key={rec.tipo}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => setSelectedRecommendation(rec)}
                className={`cursor-pointer bg-card border rounded-xl p-6 transition-all ${
                  selectedRecommendation?.tipo === rec.tipo
                    ? "border-primary shadow-lg shadow-primary/20"
                    : "border-border hover:border-primary/50"
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground capitalize mb-1">Lista {rec.tipo}</h3>
                    <p className="text-2xl font-bold text-primary">{rec.total.toFixed(2)} Bs.</p>
                  </div>
                  {selectedRecommendation?.tipo === rec.tipo && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-5 h-5 text-primary-foreground" />
                    </div>
                  )}
                </div>

                <p className="text-sm text-muted-foreground mb-4">{rec.mensaje}</p>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Productos diferentes:</span>
                    <span className="text-foreground font-medium">{rec.cantidad_productos_diferentes}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Items totales:</span>
                    <span className="text-foreground font-medium">{rec.cantidad_items}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Diferencia:</span>
                    <span className={rec.diferencia >= 0 ? "text-accent font-medium" : "text-primary font-medium"}>
                      {rec.diferencia >= 0 ? "+" : ""}
                      {rec.diferencia.toFixed(2)} Bs.
                    </span>
                  </div>
                </div>

                {/* Product list preview */}
                <div className="border-t border-border pt-4">
                  <p className="text-xs text-muted-foreground mb-2">Productos incluidos:</p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {rec.productos.slice(0, 3).map((p) => (
                      <div key={p.id} className="flex justify-between text-xs">
                        <span className="text-foreground truncate">
                          {p.cantidad}x {p.nombre}
                        </span>
                        <span className="text-muted-foreground ml-2">{p.subtotal.toFixed(2)}</span>
                      </div>
                    ))}
                    {rec.productos.length > 3 && (
                      <p className="text-xs text-muted-foreground italic">
                        +{rec.productos.length - 3} productos más...
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {selectedRecommendation && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center pt-6"
            >
              <button
                onClick={handleSelectRecommendation}
                className="flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-xl font-semibold hover:opacity-90 transition-opacity"
              >
                <ShoppingBag className="w-5 h-5" />
                Iniciar compra con esta lista
                <ChevronRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}
