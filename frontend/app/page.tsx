"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Store, ShoppingCart, Bot } from "lucide-react"
import Link from "next/link"

interface Sucursal {
  sucursal_id: string
  nombre: string
  productos_disponibles: number
  estado: string
}

export default function HomePage() {
  const [sucursales, setSucursales] = useState<Sucursal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:5000/api/sucursales")
      .then((res) => res.json())
      .then((data) => {
        setSucursales(data.sucursales || [])
        setLoading(false)
      })
      .catch((error) => {
        console.error("[v0] Error fetching sucursales:", error)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 border border-primary/20">
              <Bot className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-foreground">Sistema Multi-Agente</h1>
              <p className="text-sm text-muted-foreground">Compras inteligentes con IA</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 container mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-foreground mb-4 text-balance">Selecciona una Sucursal</h2>
            <p className="text-lg text-muted-foreground text-balance">
              Elige la sucursal donde deseas realizar tu compra y observa al agente en acción
            </p>
          </div>

          {loading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {sucursales.map((sucursal, index) => (
                <motion.div
                  key={sucursal.sucursal_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Link href={`/sucursal/${sucursal.sucursal_id}`}>
                    <div className="group relative bg-card border border-border rounded-xl p-8 hover:border-primary/50 transition-all cursor-pointer overflow-hidden">
                      {/* Glow effect on hover */}
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                      <div className="relative">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center justify-center w-14 h-14 rounded-lg bg-primary/10 border border-primary/20">
                            <Store className="w-7 h-7 text-primary" />
                          </div>
                          <div
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              sucursal.estado === "activo"
                                ? "bg-primary/10 text-primary border border-primary/20"
                                : "bg-muted text-muted-foreground border border-border"
                            }`}
                          >
                            {sucursal.estado === "activo" ? "Activo" : "Inactivo"}
                          </div>
                        </div>

                        <h3 className="text-2xl font-semibold text-foreground mb-2">{sucursal.nombre}</h3>

                        <div className="flex items-center gap-2 text-muted-foreground">
                          <ShoppingCart className="w-4 h-4" />
                          <span className="text-sm">{sucursal.productos_disponibles} productos disponibles</span>
                        </div>

                        <div className="mt-6 flex items-center text-primary font-medium group-hover:gap-2 transition-all">
                          <span>Ingresar a sucursal</span>
                          <span className="inline-block group-hover:translate-x-1 transition-transform">→</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Sistema desarrollado con Next.js y Flask - WebSocket en tiempo real
          </p>
        </div>
      </footer>
    </div>
  )
}
