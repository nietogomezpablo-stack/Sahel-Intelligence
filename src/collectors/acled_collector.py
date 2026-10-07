import getpass
import requests

TOKEN_URL = "https://acleddata.com/oauth/token"
API_URL = "https://acleddata.com/api/acled/read"

username = input("Correo de myACLED: ")
password = getpass.getpass("Contraseña de myACLED: ")

auth_data = {
    "username": username,
    "password": password,
    "grant_type": "password",
    "client_id": "acled",
    "scope": "authenticated"
}

response = requests.post(
    TOKEN_URL,
    data=auth_data,
    timeout=30
)

if response.status_code != 200:
    print("Error de autenticación:", response.status_code)
    print(response.text)
    raise SystemExit

token_data = response.json()
access_token = token_data["access_token"]

print()
print("Autenticación correcta.")
print("Token OAuth recibido correctamente.")

headers = {
    "Authorization": f"Bearer {access_token}"
}

params = {
    "country": "Niger",
    "limit": 10
}

response = requests.get(
    API_URL,
    headers=headers,
    params=params,
    timeout=30
)

if response.status_code != 200:
    print("Error consultando ACLED:", response.status_code)
    print(response.text)
    raise SystemExit

data = response.json()

events = data.get("data", [])

print()
print("Eventos recibidos:", len(events))
print()

for event in events:
    print("FECHA:", event.get("event_date"))
    print("TIPO:", event.get("event_type"))
    print("SUBTIPO:", event.get("sub_event_type"))
    print("ACTOR 1:", event.get("actor1"))
    print("ACTOR 2:", event.get("actor2"))
    print("PAÍS:", event.get("country"))
    print("REGIÓN:", event.get("admin1"))
    print("LOCALIDAD:", event.get("location"))
    print("LATITUD:", event.get("latitude"))
    print("LONGITUD:", event.get("longitude"))
    print("MUERTES:", event.get("fatalities"))
    print("NOTAS:", event.get("notes"))
    print("-" * 80)
