"use client"

import { useEffect, useState, use } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowLeft, Bot, ShoppingCart, TrendingUp, Loader2 } from "lucide-react"
import Link from "next/link"
import { api, type RecommendationResponse, type MapData, type ShoppingResult } from "@/lib/api"
import RecommenderView from "@/components/RecommenderView"
import ShoppingView from "@/components/ShoppingView"
import FinalReport from "@/components/FinalReport"

type Step = "arriving" | "recommender" | "shopping" | "complete"

export default function SucursalPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const sucursalId = resolvedParams.id

  const [step, setStep] = useState<Step>("arriving")
  const [mapData, setMapData] = useState<MapData | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null)
  const [selectedProducts, setSelectedProducts] = useState<Array<{ id: number; nombre: string; cantidad: number }>>([])
  const [compradorId, setCompradorId] = useState<string>("")
  const [shoppingResult, setShoppingResult] = useState<ShoppingResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load map data
    const loadInitialData = async () => {
      try {
        const map = await api.getMap(sucursalId)
        setMapData(map)

        // Create buyer agent
        const buyer = await api.createBuyer(sucursalId)
        setCompradorId(buyer.comprador_id)

        // Simulate arrival
        setTimeout(() => {
          setStep("recommender")
          setLoading(false)
        }, 2000)
      } catch (error) {
        console.error("[v0] Error loading initial data:", error)
        setLoading(false)
      }
    }

    loadInitialData()
  }, [sucursalId])

  const handleBudgetSubmit = async (presupuesto: number) => {
    try {
      const recs = await api.getRecommendations(sucursalId, presupuesto)
      setRecommendations(recs)
    } catch (error) {
      console.error("[v0] Error getting recommendations:", error)
    }
  }

  const handleProductSelection = (products: Array<{ id: number; nombre: string; cantidad: number }>) => {
    setSelectedProducts(products)
    setStep("shopping")
  }

  const handleShoppingComplete = (result: ShoppingResult) => {
    setShoppingResult(result)
    setStep("complete")
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 border border-primary/20 mb-4">
            <Bot className="w-8 h-8 text-primary animate-pulse" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">Ingresando a la sucursal...</h2>
          <p className="text-muted-foreground">El agente comprador está llegando</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span className="text-sm font-medium">Volver</span>
              </Link>
              <div className="h-6 w-px bg-border" />
              <h1 className="text-lg font-semibold text-foreground">{mapData?.nombre || "Sucursal"}</h1>
            </div>

            {/* Step indicator */}
            <div className="flex items-center gap-3">
              <StepIndicator active={step === "arriving" || step === "recommender"} icon={Bot} label="Recomendador" />
              <div className="w-8 h-px bg-border" />
              <StepIndicator active={step === "shopping"} icon={ShoppingCart} label="Comprando" />
              <div className="w-8 h-px bg-border" />
              <StepIndicator active={step === "complete"} icon={TrendingUp} label="Completado" />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {step === "arriving" && (
            <motion.div
              key="arriving"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center min-h-[60vh]"
            >
              <div className="text-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-foreground mb-2">Ingresando...</h2>
                <p className="text-muted-foreground">El agente está entrando a la sucursal</p>
              </div>
            </motion.div>
          )}

          {step === "recommender" && (
            <RecommenderView
              sucursalId={sucursalId}
              onBudgetSubmit={handleBudgetSubmit}
              recommendations={recommendations}
              onProductSelection={handleProductSelection}
            />
          )}

          {step === "shopping" && mapData && (
            <ShoppingView
              compradorId={compradorId}
              sucursalId={sucursalId}
              mapData={mapData}
              selectedProducts={selectedProducts}
              onComplete={handleShoppingComplete}
            />
          )}

          {step === "complete" && shoppingResult && <FinalReport result={shoppingResult} />}
        </AnimatePresence>
      </main>
    </div>
  )
}

function StepIndicator({ active, icon: Icon, label }: { active: boolean; icon: any; label: string }) {
  return (
    <div className={`flex items-center gap-2 ${active ? "text-primary" : "text-muted-foreground"}`}>
      <div
        className={`flex items-center justify-center w-8 h-8 rounded-full border ${
          active ? "bg-primary/10 border-primary" : "bg-muted border-border"
        }`}
      >
        <Icon className="w-4 h-4" />
      </div>
      <span className="text-sm font-medium hidden md:block">{label}</span>
    </div>
  )
}
