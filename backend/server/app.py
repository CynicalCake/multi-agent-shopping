"""
Servidor Flask para el Sistema Multi-Agente de Supermercado
Gestiona la comunicación entre agentes recomendadores y compradores.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import os
import sys
import json

# Agregar el directorio actual al path para imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from models.agente_recomendador import AgenteRecomendador
from models.agente_comprador import AgenteComprador

# Rutas de datos
DATA_DIR = os.path.join(BASE_DIR, "data")
MAPAS_DIR = os.path.join(DATA_DIR, "mapas")
INVENTARIO_DIR = os.path.join(DATA_DIR, "inventario")

app = Flask(__name__)
app.config["SECRET_KEY"] = "supermercado_ia_2025"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Diccionario para mantener los agentes recomendadores activos
agentes_recomendadores = {}

# Diccionario para mantener los agentes compradores activos
agentes_compradores = {}


def _discover_sucursales() -> list[str]:
    """
    Descubre sucursales disponibles leyendo archivos JSON:
    - Debe existir SUCxxx.json en /data/inventario y /data/mapas
    """
    try:
        inv_ids = {
            os.path.splitext(f)[0]
            for f in os.listdir(INVENTARIO_DIR)
            if f.lower().endswith(".json")
        } if os.path.exists(INVENTARIO_DIR) else set()

        map_ids = {
            os.path.splitext(f)[0]
            for f in os.listdir(MAPAS_DIR)
            if f.lower().endswith(".json")
        } if os.path.exists(MAPAS_DIR) else set()

        return sorted(list(inv_ids.intersection(map_ids)))
    except Exception:
        # Si algo falla, volvemos a un fallback mínimo
        return ["SUC001", "SUC002"]


def inicializar_agentes_recomendadores():
    """
    Inicializa los agentes recomendadores para todas las sucursales disponibles.
    """
    print("\n" + "=" * 60)
    print("INICIALIZANDO SISTEMA MULTI-AGENTE DE SUPERMERCADO")
    print("=" * 60)

    sucursales = _discover_sucursales()
    if not sucursales:
        sucursales = ["SUC001", "SUC002"]

    for sucursal_id in sucursales:
        try:
            agente = AgenteRecomendador(sucursal_id)
            agentes_recomendadores[sucursal_id] = agente
            print(f"✓ Agente recomendador activo en {agente.nombre_sucursal}")
        except Exception as e:
            print(f"✗ Error al inicializar agente en {sucursal_id}: {e}")

    print("=" * 60)
    print(f"Total de agentes recomendadores activos: {len(agentes_recomendadores)}")
    print("=" * 60 + "\n")


# ============================================================================
# ENDPOINTS REST API
# ============================================================================

@app.route("/")
def index():
    """Endpoint raíz con información del sistema."""
    return jsonify({
        "sistema": "Sistema Multi-Agente de Supermercado",
        "version": "2.0.1",
        "agentes_recomendadores_activos": len(agentes_recomendadores),
        "agentes_compradores_activos": len(agentes_compradores),
        "sucursales_disponibles": list(agentes_recomendadores.keys()),
        "endpoints": {
            "recomendaciones": "/api/recomendador/solicitar",
            "estado_recomendador": "/api/recomendador/estado/<sucursal_id>",
            "crear_comprador": "/api/comprador/crear",
            "iniciar_compra": "/api/comprador/iniciar_compra",
            "compra_completa": "/api/comprador/compra_completa",
            "estado_comprador": "/api/comprador/estado/<comprador_id>",
            "inventario": "/api/sucursal/<sucursal_id>/inventario",
            "mapa": "/api/sucursal/<sucursal_id>/mapa",
            "sucursales": "/api/sucursales"
        }
    })


@app.route("/api/sucursales", methods=["GET"])
def listar_sucursales():
    """Lista todas las sucursales disponibles."""
    sucursales = []
    for sucursal_id, agente in agentes_recomendadores.items():
        sucursales.append({
            "sucursal_id": sucursal_id,
            "nombre": agente.nombre_sucursal,
            "productos_disponibles": len(getattr(agente, "productos", [])),
            "estado": getattr(agente, "estado", "desconocido")
        })

    return jsonify({
        "total": len(sucursales),
        "sucursales": sucursales
    })


@app.route("/api/sucursal/<sucursal_id>/inventario", methods=["GET"])
def obtener_inventario(sucursal_id):
    """Obtiene el inventario completo de una sucursal."""
    if sucursal_id not in agentes_recomendadores:
        return jsonify({"error": f"Sucursal {sucursal_id} no encontrada"}), 404

    agente = agentes_recomendadores[sucursal_id]
    try:
        return jsonify(agente.obtener_inventario()), 200
    except Exception as e:
        return jsonify({
            "error": "Error al obtener inventario",
            "detalle": str(e)
        }), 500


@app.route("/api/sucursal/<sucursal_id>/mapa", methods=["GET"])
def obtener_mapa(sucursal_id):
    """Obtiene el mapa de una sucursal desde JSON."""
    ruta_mapa = os.path.join(MAPAS_DIR, f"{sucursal_id}.json")

    try:
        with open(ruta_mapa, "r", encoding="utf-8") as archivo:
            return jsonify(json.load(archivo)), 200
    except FileNotFoundError:
        return jsonify({"error": f"Mapa de {sucursal_id} no encontrado"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": f"Error al decodificar el mapa de {sucursal_id}"}), 500
    except Exception as e:
        return jsonify({"error": "Error al leer mapa", "detalle": str(e)}), 500


@app.route("/api/recomendador/estado/<sucursal_id>", methods=["GET"])
def estado_recomendador(sucursal_id):
    """Obtiene el estado del agente recomendador de una sucursal."""
    if sucursal_id not in agentes_recomendadores:
        return jsonify({"error": f"Agente recomendador no encontrado para {sucursal_id}"}), 404

    agente = agentes_recomendadores[sucursal_id]
    return jsonify(agente.obtener_estado()), 200


@app.route("/api/recomendador/solicitar", methods=["POST"])
def solicitar_recomendacion():
    """
    Solicita recomendaciones de compra a un agente recomendador.
    Body JSON:
    {
        "sucursal_id": "SUC001",
        "presupuesto": 100.0,
        "categorias_preferidas": ["lacteos", "panaderia"]  // Opcional
    }
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        sucursal_id = datos.get("sucursal_id")
        presupuesto = datos.get("presupuesto")
        categorias_preferidas = datos.get("categorias_preferidas", [])

        if not sucursal_id:
            return jsonify({"error": "sucursal_id es requerido"}), 400

        try:
            presupuesto = float(presupuesto)
        except Exception:
            return jsonify({"error": "presupuesto debe ser numérico"}), 400

        if presupuesto <= 0:
            return jsonify({"error": "presupuesto debe ser mayor a 0"}), 400

        if sucursal_id not in agentes_recomendadores:
            return jsonify({"error": f"Agente recomendador no encontrado para {sucursal_id}"}), 404

        agente = agentes_recomendadores[sucursal_id]
        recomendaciones = agente.generar_recomendaciones(
            presupuesto=presupuesto,
            categorias_preferidas=categorias_preferidas if categorias_preferidas else None
        )

        return jsonify(recomendaciones), 200

    except Exception as e:
        return jsonify({"error": "Error al procesar solicitud", "detalle": str(e)}), 500


@app.route("/api/comprador/crear", methods=["POST"])
def crear_comprador():
    """
    Crea un nuevo agente comprador y opcionalmente lo ingresa a una sucursal.
    Body JSON:
    {
        "comprador_id": "COMP001",  // Opcional
        "sucursal_id": "SUC001"     // Opcional
    }
    """
    try:
        datos = request.get_json() or {}
        comprador_id = datos.get("comprador_id", f"COMP{len(agentes_compradores) + 1:03d}")
        sucursal_id = datos.get("sucursal_id")

        if comprador_id in agentes_compradores:
            return jsonify({"error": f"Ya existe un comprador con ID {comprador_id}"}), 400

        agente = AgenteComprador(comprador_id)
        agentes_compradores[comprador_id] = agente

        if sucursal_id:
            if sucursal_id not in agentes_recomendadores:
                return jsonify({"error": f"Sucursal {sucursal_id} no encontrada"}), 404
            agente.ingresar_a_sucursal(sucursal_id)

        estado = agente.obtener_estado()
        return jsonify({
            "mensaje": "Comprador creado exitosamente" + (" e ingresado a sucursal" if sucursal_id else ""),
            "comprador_id": comprador_id,
            "sucursal_id": estado["sucursal_id"],
            "sucursal_nombre": estado["sucursal_nombre"],
            "estado": estado["estado"],
            "posicion_actual": estado["posicion_actual"]
        }), 201

    except Exception as e:
        return jsonify({"error": "Error al crear comprador", "detalle": str(e)}), 500


@app.route("/api/comprador/iniciar_compra", methods=["POST"])
def iniciar_compra():
    """
    Inicia el proceso de compra para un comprador.
    Puede recibir presupuesto o lista_compras.
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        comprador_id = datos.get("comprador_id")
        sucursal_id = datos.get("sucursal_id")

        if not comprador_id:
            return jsonify({"error": "comprador_id es requerido"}), 400
        if not sucursal_id:
            return jsonify({"error": "sucursal_id es requerido"}), 400

        if comprador_id not in agentes_compradores:
            return jsonify({
                "error": f"Comprador {comprador_id} no encontrado. Crear primero con /api/comprador/crear"
            }), 404

        agente_comprador = agentes_compradores[comprador_id]

        if agente_comprador.estado in ["comprando", "finalizado"]:
            return jsonify({
                "mensaje": f"Compra ya {agente_comprador.estado}",
                "comprador_id": comprador_id,
                "sucursal_id": sucursal_id,
                "estado": agente_comprador.obtener_estado()
            }), 200

        # Ingresar/reingresar
        agente_comprador.ingresar_a_sucursal(sucursal_id)

        lista_compras = datos.get("lista_compras")

        if not lista_compras:
            presupuesto = datos.get("presupuesto")
            categorias_preferidas = datos.get("categorias_preferidas", [])

            if presupuesto is None:
                return jsonify({"error": 'Debe proporcionar "lista_compras" o "presupuesto"'}), 400

            try:
                presupuesto = float(presupuesto)
            except Exception:
                return jsonify({"error": "presupuesto debe ser numérico"}), 400

            if presupuesto <= 0:
                return jsonify({"error": "presupuesto debe ser mayor a 0"}), 400

            if sucursal_id not in agentes_recomendadores:
                return jsonify({"error": f"Agente recomendador no encontrado para {sucursal_id}"}), 404

            agente_recomendador = agentes_recomendadores[sucursal_id]
            recomendaciones = agente_recomendador.generar_recomendaciones(
                presupuesto=presupuesto,
                categorias_preferidas=categorias_preferidas if categorias_preferidas else None
            )

            rec_exacta = next(r for r in recomendaciones["recomendaciones"] if r["tipo"] == "exacta")
            lista_compras = rec_exacta["productos"]

        agente_comprador.planificar_compra(lista_compras)

        return jsonify({
            "mensaje": "Compra iniciada y planificada",
            "comprador_id": comprador_id,
            "sucursal_id": sucursal_id,
            "estado": agente_comprador.obtener_estado()
        }), 200

    except Exception as e:
        return jsonify({"error": "Error al iniciar compra", "detalle": str(e)}), 500


@app.route("/api/comprador/compra_completa", methods=["POST"])
def compra_completa():
    """Ejecuta y completa la compra del comprador."""
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        comprador_id = datos.get("comprador_id")
        if not comprador_id:
            return jsonify({"error": "comprador_id es requerido"}), 400

        if comprador_id not in agentes_compradores:
            return jsonify({"error": f"Comprador {comprador_id} no encontrado"}), 404

        agente = agentes_compradores[comprador_id]

        if agente.estado == "finalizado":
            return jsonify({
                "comprador_id": agente.comprador_id,
                "sucursal_id": agente.sucursal_id,
                "sucursal_nombre": agente.mapa_sucursal["nombre"] if agente.mapa_sucursal else None,
                "productos_recolectados": agente.productos_recolectados,
                "ruta_detallada": agente._generar_ruta_detallada(),
                "distancia_total": agente.distancia_total,
                "total_items": sum(p["cantidad"] for p in agente.productos_recolectados),
                "tiempo_estimado": agente._estimar_tiempo(),
                "posicion_final": agente.posicion_actual,
                "estado": agente.estado
            }), 200

        resultado = agente.ejecutar_compra()
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": "Error al completar compra", "detalle": str(e)}), 500


@app.route("/api/comprador/estado/<comprador_id>", methods=["GET"])
def estado_comprador(comprador_id):
    """Obtiene el estado de un agente comprador."""
    if comprador_id not in agentes_compradores:
        return jsonify({"error": f"Comprador {comprador_id} no encontrado"}), 404

    agente = agentes_compradores[comprador_id]
    return jsonify(agente.obtener_estado()), 200


@app.route("/api/comprador/flujo_completo", methods=["POST"])
def flujo_completo():
    """Flujo completo: crear comprador, recomendar, planificar y ejecutar."""
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        sucursal_id = datos.get("sucursal_id")
        presupuesto = datos.get("presupuesto")
        categorias_preferidas = datos.get("categorias_preferidas", [])

        if not sucursal_id or presupuesto is None:
            return jsonify({"error": "sucursal_id y presupuesto son requeridos"}), 400

        try:
            presupuesto = float(presupuesto)
        except Exception:
            return jsonify({"error": "presupuesto debe ser numérico"}), 400

        if presupuesto <= 0:
            return jsonify({"error": "presupuesto debe ser mayor a 0"}), 400

        comprador_id = f"COMP{len(agentes_compradores) + 1:03d}"
        agente_comprador = AgenteComprador(comprador_id)
        agentes_compradores[comprador_id] = agente_comprador

        if sucursal_id not in agentes_recomendadores:
            return jsonify({"error": f"Agente recomendador no encontrado para {sucursal_id}"}), 404

        agente_recomendador = agentes_recomendadores[sucursal_id]
        recomendaciones = agente_recomendador.generar_recomendaciones(
            presupuesto=presupuesto,
            categorias_preferidas=categorias_preferidas if categorias_preferidas else None
        )

        agente_comprador.ingresar_a_sucursal(sucursal_id)

        rec_exacta = next(r for r in recomendaciones["recomendaciones"] if r["tipo"] == "exacta")
        agente_comprador.planificar_compra(rec_exacta["productos"])

        resultado_compra = agente_comprador.ejecutar_compra()

        return jsonify({
            "comprador_id": comprador_id,
            "sucursal_id": sucursal_id,
            "sucursal_nombre": recomendaciones["sucursal_nombre"],
            "recomendacion": rec_exacta,
            "navegacion": resultado_compra
        }), 200

    except Exception as e:
        return jsonify({"error": "Error en flujo completo", "detalle": str(e)}), 500


# ============================================================================
# WEBSOCKETS - Para mantener agentes reactivos
# ============================================================================

@socketio.on("connect")
def handle_connect():
    print(f"[WebSocket] Cliente conectado: {request.sid}")
    emit("connection_response", {
        "status": "connected",
        "message": "Conectado al sistema de agentes",
        "agentes_disponibles": list(agentes_recomendadores.keys())
    })


@socketio.on("disconnect")
def handle_disconnect():
    print(f"[WebSocket] Cliente desconectado: {request.sid}")


@socketio.on("registrar_recomendador")
def handle_registrar_recomendador(data):
    sucursal_id = data.get("sucursal_id")
    if sucursal_id in agentes_recomendadores:
        join_room(f"recomendador_{sucursal_id}")
        emit("registro_exitoso", {
            "sucursal_id": sucursal_id,
            "mensaje": f"Registrado en sala del agente recomendador {sucursal_id}"
        })
        print(f"[WebSocket] Agente recomendador {sucursal_id} registrado en sala")
    else:
        emit("error", {"mensaje": f"Sucursal {sucursal_id} no encontrada"})


@socketio.on("solicitar_recomendacion_ws")
def handle_solicitar_recomendacion_ws(data):
    try:
        sucursal_id = data.get("sucursal_id")
        presupuesto = data.get("presupuesto")
        categorias_preferidas = data.get("categorias_preferidas", [])

        if sucursal_id not in agentes_recomendadores:
            emit("error", {"mensaje": f"Agente no encontrado para {sucursal_id}"})
            return

        try:
            presupuesto = float(presupuesto)
        except Exception:
            emit("error", {"mensaje": "presupuesto debe ser numérico"})
            return

        agente = agentes_recomendadores[sucursal_id]
        recomendaciones = agente.generar_recomendaciones(
            presupuesto=presupuesto,
            categorias_preferidas=categorias_preferidas if categorias_preferidas else None
        )

        emit("recomendaciones_generadas", recomendaciones)
        print(f"[WebSocket] Recomendaciones enviadas para {sucursal_id}")

    except Exception as e:
        emit("error", {
            "mensaje": "Error al generar recomendaciones",
            "detalle": str(e)
        })


# ============================================================================
# INICIALIZACIÓN Y EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    inicializar_agentes_recomendadores()

    print("\n🚀 Servidor Flask iniciado")
    print("📍 URL: http://localhost:5000")
    print("🔌 WebSocket habilitado")
    print("\nPresiona Ctrl+C para detener el servidor\n")

    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
