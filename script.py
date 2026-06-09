import os
import requests
from datetime import datetime
import pytz

def leer_fechas(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return []
    with open(nombre_archivo, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# 1. Configurar zona horaria y obtener fecha
lima_tz = pytz.timezone('America/Lima')
today = datetime.now(lima_tz)
date_str = today.strftime('%Y-%m-%d')

print(f"Ejecutando marcación para el día: {date_str}")

# 2. Validar si ya se marcó hoy (Evitar duplicados)
marcados = leer_fechas('marcados.txt')
if date_str in marcados:
    print("✅ El día de hoy ya fue marcado anteriormente. Omitiendo petición.")
    exit(0)

# 3. Validar fines de semana (5 = Sábado, 6 = Domingo)
if today.weekday() >= 5:
    print("Es fin de semana. No se ejecuta la marcación.")
    exit(0)

# 4. Validar Feriados
feriados = leer_fechas('feriados.txt')
if date_str in feriados:
    print("Es feriado. No se ejecuta la marcación.")
    exit(0)

# 5. Validar Vacaciones
vacaciones = leer_fechas('vacaciones.txt')
if date_str in vacaciones:
    print("Estás de vacaciones. No se ejecuta la marcación.")
    exit(0)

# 6. Determinar Modalidad
presenciales = leer_fechas('presenciales.txt')
site = "Presencial" if date_str in presenciales else "Remoto"
print(f"Modalidad del día: {site}")

# 7. Preparar Request
start_ts = f"{date_str}T08:30"
end_ts = f"{date_str}T17:00"

url = "https://request-workflow-api.rankmi.com/api/v1/requests"
token = os.environ.get("RANKMI_TOKEN")

if not token:
    print("Error crítico: No se encontró el TOKEN en las variables de entorno.")
    exit(1)

headers = {
    "accept": "application/json, text/plain, */*",
    "authorization": f"Bearer {token}",
    "content-type": "application/json",
    "origin": "https://app.rankmi.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

payload = {
    "workflow_configuration_id": 1218,
    "data": {
        "field_id_1749753234721": site,
        "field_id_1749753276831": start_ts,
        "field_id_1750089911720": end_ts,
        "optionals": {}
    }
}

# 8. Ejecutar Petición
response = requests.post(url, json=payload, headers=headers)

# 9. Validar respuesta y guardar registro
if response.status_code in (200, 201):
    # Guardar la fecha en marcados.txt solo si fue exitoso
    with open('marcados.txt', 'a') as f:
        f.write(date_str + '\n')
    print("✅ Marcación registrada exitosamente y guardada en marcados.txt.")
else:
    print(f"❌ Error en la API de Rankmi. Código HTTP: {response.status_code}")
    print(response.text)
    exit(1)