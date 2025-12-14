# Configuración del Proyecto

## Configuración del Entorno Virtual (Recomendado)

### Windows (PowerShell)
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias
pip install -r server\requirements.txt
```

### Windows (CMD)
```cmd
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r server\requirements.txt
```

### Linux/Mac
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r server/requirements.txt
```

## Ejecutar el Proyecto

### 1. Ejecutar pruebas del agente recomendador
```bash
python test_agente_recomendador.py
```

### 2. Iniciar el servidor Flask
```bash
cd server
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

### 3. Probar la API con ejemplos
En otra terminal (con el servidor ejecutándose):
```bash
# Instalar requests si no está instalado
pip install requests

# Ejecutar ejemplos
python ejemplos_api.py
```

## Probar con cURL

### Listar sucursales
```bash
curl http://localhost:5000/api/sucursales
```

### Obtener inventario
```bash
curl http://localhost:5000/api/sucursal/SUC001/inventario
```

### Solicitar recomendación
```bash
curl -X POST http://localhost:5000/api/recomendador/solicitar \
  -H "Content-Type: application/json" \
  -d "{\"sucursal_id\": \"SUC001\", \"presupuesto\": 100.0}"
```

### Solicitar recomendación con categorías
```bash
curl -X POST http://localhost:5000/api/recomendador/solicitar \
  -H "Content-Type: application/json" \
  -d "{\"sucursal_id\": \"SUC001\", \"presupuesto\": 150.0, \"categorias_preferidas\": [\"lacteos\", \"panaderia\"]}"
```

## Probar con Postman

1. Importar la colección o crear las siguientes requests:

### GET - Listar Sucursales
- URL: `http://localhost:5000/api/sucursales`
- Method: GET

### POST - Solicitar Recomendación
- URL: `http://localhost:5000/api/recomendador/solicitar`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "sucursal_id": "SUC001",
  "presupuesto": 100.0,
  "categorias_preferidas": ["lacteos", "panaderia"]
}
```

## Variables de Entorno (Opcional)

Crear archivo `.env` en la raíz del proyecto:
```env
FLASK_APP=server/app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=supermercado_ia_2025
PORT=5000
```

## Troubleshooting

### Error: ModuleNotFoundError
```bash
# Asegúrate de estar en el entorno virtual
# Reinstala las dependencias
pip install -r server/requirements.txt
```

### Error: Puerto 5000 en uso
Cambia el puerto en `server/app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Error: No se encuentra el inventario
Verifica que los archivos JSON existan en:
- `server/data/inventario/SUC001.json`
- `server/data/inventario/SUC002.json`

## Estructura de Archivos Esperada

```
Propuesta v4/
├── server/
│   ├── app.py
│   ├── requirements.txt
│   ├── models/
│   │   └── agente_recomendador.py
│   ├── utils/
│   │   └── algoritmos_busqueda.py
│   └── data/
│       └── inventario/
│           ├── SUC001.json
│           └── SUC002.json
├── test_agente_recomendador.py
├── ejemplos_api.py
└── README.md
```
