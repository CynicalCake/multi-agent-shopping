"""
Generador de sucursales (mapa + inventario) para el proyecto.

Uso:
  python -m utils.generar_sucursal SUC006 "Hipermaxi - Queru Queru" 24 36 standard

Estilos:
  - compact  : supermercado pequeño con menos estantes
  - standard : tamaño medio
  - big      : tamaño grande con más estantes
"""

import os
import json
import random
import sys
from typing import Dict, Tuple, Set

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(HERE)
DATA_MAPAS = os.path.join(SERVER_DIR, "data", "mapas")
DATA_INV = os.path.join(SERVER_DIR, "data", "inventario")


def build_obstacles(rows: int, cols: int, style: str) -> Set[Tuple[int, int]]:
    obs: Set[Tuple[int, int]] = set()

    if style == "standard":
        shelf_cols = [
            int(cols * 0.15), int(cols * 0.30), int(cols * 0.45),
            int(cols * 0.60), int(cols * 0.75)
        ]
        cross_aisles = [int(rows * 0.40), int(rows * 0.65)]
    elif style == "compact":
        shelf_cols = [int(cols * 0.22), int(cols * 0.44), int(cols * 0.66)]
        cross_aisles = [int(rows * 0.45)]
    else:  # big
        shelf_cols = [
            int(cols * 0.12), int(cols * 0.24), int(cols * 0.36), int(cols * 0.48),
            int(cols * 0.60), int(cols * 0.72), int(cols * 0.84)
        ]
        cross_aisles = [int(rows * 0.33), int(rows * 0.55), int(rows * 0.75)]

    shelf_cols = [c for c in shelf_cols if 2 <= c <= cols - 3]

    cross_bands = set()
    for r in cross_aisles:
        for rr in range(max(2, r - 1), min(rows - 2, r + 2)):
            cross_bands.add(rr)

    for c in shelf_cols:
        for w in (0, 1):  # ancho estante = 2
            cc = c + w
            for r in range(2, rows - 2):
                if r in cross_bands:
                    continue
                # pasillo central (dejarlo libre)
                if abs(cc - cols // 2) <= 1:
                    continue
                obs.add((r, cc))

    # bloques horizontales "isla" (intermitentes)
    for r in (int(rows * 0.20), int(rows * 0.80)):
        for rr in range(max(2, r - 1), min(rows - 2, r + 1)):
            for c in range(2, cols - 2):
                if abs(c - cols // 2) <= 1:
                    continue
                if c % 7 in (0, 1):
                    obs.add((rr, c))

    return obs


def find_free(pos: Tuple[int, int], obs: Set[Tuple[int, int]], rows: int, cols: int) -> Tuple[int, int]:
    r, c = pos
    for d in range(0, max(rows, cols)):
        for dr in range(-d, d + 1):
            for dc in range(-d, d + 1):
                rr = r + dr
                cc = c + dc
                if 0 <= rr < rows and 0 <= cc < cols and (rr, cc) not in obs:
                    return rr, cc
    return r, c


def load_template(template_id: str = "SUC002") -> Tuple[Dict, Dict]:
    with open(os.path.join(DATA_MAPAS, f"{template_id}.json"), "r", encoding="utf-8") as f:
        tpl_map = json.load(f)
    with open(os.path.join(DATA_INV, f"{template_id}.json"), "r", encoding="utf-8") as f:
        tpl_inv = json.load(f)
    return tpl_map, tpl_inv


def build_zones(rows: int, cols: int, obs: Set[Tuple[int, int]], zone_products: Dict[str, list]) -> Dict:
    anchors = {
        "lacteos": (0.22, 0.18),
        "panaderia": (0.12, 0.78),
        "granos": (0.30, 0.30),
        "aceites": (0.30, 0.70),
        "endulzantes": (0.38, 0.16),
        "condimentos": (0.38, 0.82),
        "limpieza": (0.72, 0.84),
        "carnes": (0.55, 0.50),
        "verduras": (0.60, 0.22),
        "frutas": (0.60, 0.78),
        "enlatados": (0.48, 0.30),
        "bebidas": (0.78, 0.50),
        "snacks": (0.48, 0.70),
        "caramelos": (0.20, 0.50),
        "desayuno": (0.18, 0.30),
    }

    zonas = {}
    for cat, (fr, fc) in anchors.items():
        r = int(rows * fr)
        c = int(cols * fc)
        rr, cc = find_free((r, c), obs, rows, cols)
        zonas[cat] = {"fila": rr, "columna": cc, "productos": zone_products.get(cat, [])}

    # fallback
    for cat in zone_products.keys():
        if cat not in zonas:
            rr, cc = find_free((rows // 2, cols // 2), obs, rows, cols)
            zonas[cat] = {"fila": rr, "columna": cc, "productos": zone_products[cat]}

    return zonas


def build_pasillos(rows: int, cols: int, obs: Set[Tuple[int, int]]):
    pas = []
    # pasillo central
    for r in range(rows):
        for c in range(cols):
            if (r, c) in obs:
                continue
            if abs(c - cols // 2) <= 1:
                pas.append({"fila": r, "columna": c, "tipo": "pasillo"})

    # cruces horizontales
    for r in (int(rows * 0.40), int(rows * 0.65)):
        for c in range(cols):
            if (r, c) in obs:
                continue
            pas.append({"fila": r, "columna": c, "tipo": "pasillo"})

    # de-dup
    seen = set()
    out = []
    for p in pas:
        k = (p["fila"], p["columna"])
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def generar_sucursal(sucursal_id: str, nombre: str, rows: int, cols: int, style: str, template_id: str = "SUC002"):
    tpl_map, tpl_inv = load_template(template_id)
    categories = list(tpl_map["zonas_productos"].keys())

    obs = build_obstacles(rows, cols, style)
    entrada = find_free((0, cols // 2), obs, rows, cols)
    caja = find_free((rows - 1, cols // 2), obs, rows, cols)
    obs.discard(entrada)
    obs.discard(caja)

    zone_products = {cat: tpl_map["zonas_productos"][cat]["productos"] for cat in categories}
    zonas = build_zones(rows, cols, obs, zone_products)
    for info in zonas.values():
        obs.discard((info["fila"], info["columna"]))

    mapa = {
        "sucursal_id": sucursal_id,
        "nombre": nombre,
        "dimensiones": {"filas": rows, "columnas": cols},
        "entrada": {"fila": entrada[0], "columna": entrada[1], "tipo": "entrada"},
        "caja": {"fila": caja[0], "columna": caja[1], "tipo": "caja"},
        "zonas_productos": zonas,
        "obstaculos": [{"fila": r, "columna": c, "tipo": "estante"} for (r, c) in sorted(obs)],
        "pasillos": build_pasillos(rows, cols, obs),
        "descripcion": f"Mapa generado ({style}) con estantes tipo isla y pasillos centrales.",
    }

    # inventario: copiar productos del template y variar un poco precios (determinista por sucursal_id)
    rnd = random.Random(hash(sucursal_id) & 0xFFFFFFFF)
    productos = []
    for prod in tpl_inv["productos"]:
        p = dict(prod)
        factor = 1 + rnd.uniform(-0.08, 0.08)
        p["precio"] = round(p["precio"] * factor, 2)
        productos.append(p)

    inv = {"sucursal_id": sucursal_id, "nombre": nombre, "productos": productos}

    os.makedirs(DATA_MAPAS, exist_ok=True)
    os.makedirs(DATA_INV, exist_ok=True)

    with open(os.path.join(DATA_MAPAS, f"{sucursal_id}.json"), "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA_INV, f"{sucursal_id}.json"), "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=2)

    print(f"✓ Generado {sucursal_id}: {nombre}")
    print(f"  - Mapa: {os.path.join(DATA_MAPAS, sucursal_id + '.json')}")
    print(f"  - Inventario: {os.path.join(DATA_INV, sucursal_id + '.json')}")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print('Uso: python -m utils.generar_sucursal SUC006 "Nombre" filas columnas estilo')
        sys.exit(1)
    sid = sys.argv[1]
    nombre = sys.argv[2]
    filas = int(sys.argv[3])
    columnas = int(sys.argv[4])
    estilo = sys.argv[5]
    generar_sucursal(sid, nombre, filas, columnas, estilo)
