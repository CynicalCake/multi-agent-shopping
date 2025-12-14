"use client"

import { motion } from "framer-motion"
import { CheckCircle, Package, Navigation, Clock, TrendingUp, Home } from "lucide-react"
import Link from "next/link"
import type { ShoppingResult } from "@/lib/api"

interface Props {
  result: ShoppingResult
}

export default function FinalReport({ result }: Props) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-4xl mx-auto">
      {/* Success header */}
      <div className="text-center mb-12">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", duration: 0.6 }}
          className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary mb-6"
        >
          <CheckCircle className="w-10 h-10 text-primary-foreground" />
        </motion.div>
        <h2 className="text-4xl font-bold text-foreground mb-4">Compra Completada</h2>
        <p className="text-lg text-muted-foreground">
          El agente ha finalizado exitosamente la compra en {result.sucursal_nombre}
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <StatCard
          icon={Package}
          label="Productos"
          value={result.productos_recolectados.length.toString()}
          color="primary"
        />
        <StatCard icon={TrendingUp} label="Items Totales" value={result.total_items.toString()} color="accent" />
        <StatCard icon={Navigation} label="Distancia" value={`${result.distancia_total} pasos`} color="primary" />
        <StatCard icon={Clock} label="Tiempo" value={result.tiempo_estimado} color="accent" />
      </div>

      {/* Products collected */}
      <div className="bg-card border border-border rounded-xl p-8 mb-8">
        <h3 className="text-2xl font-semibold text-foreground mb-6">Productos Recolectados</h3>
        <div className="grid gap-4 md:grid-cols-2">
          {result.productos_recolectados.map((producto, index) => (
            <motion.div
              key={producto.producto_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center gap-4 p-4 bg-muted rounded-lg border border-border"
            >
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex-shrink-0">
                <Package className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground truncate">{producto.nombre}</p>
                <p className="text-sm text-muted-foreground">Cantidad: {producto.cantidad}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Route summary */}
      <div className="bg-card border border-border rounded-xl p-8 mb-8">
        <h3 className="text-2xl font-semibold text-foreground mb-6">Resumen de Ruta</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {result.ruta_detallada.map((step, index) => (
            <div key={step.paso} className="flex items-start gap-4 p-4 bg-muted rounded-lg border border-border">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-background text-foreground text-sm font-medium flex-shrink-0">
                {step.paso}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-foreground">
                    {step.accion === "inicio" && "Inicio"}
                    {step.accion === "avanzar" && "Avanzar"}
                    {step.accion === "recoger_producto" && "Recoger producto"}
                    {step.accion === "caja" && "Llegar a caja"}
                  </span>
                </div>
                {step.producto && (
                  <p className="text-sm text-muted-foreground">
                    {step.producto.cantidad}x {step.producto.nombre}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Posición: [{step.posicion[0]}, {step.posicion[1]}]
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <Link href="/">
          <button className="flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-xl font-semibold hover:opacity-90 transition-opacity">
            <Home className="w-5 h-5" />
            Volver al inicio
          </button>
        </Link>
      </div>
    </motion.div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: any
  label: string
  value: string
  color: "primary" | "accent"
}) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <div
        className={`inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4 ${
          color === "primary" ? "bg-primary/10 border border-primary/20" : "bg-accent/10 border border-accent/20"
        }`}
      >
        <Icon className={`w-6 h-6 ${color === "primary" ? "text-primary" : "text-accent"}`} />
      </div>
      <p className="text-2xl font-bold text-foreground mb-1">{value}</p>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  )
}
