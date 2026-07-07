#este es un script hechjo para dejar de llenar forms enormes jaja just for fun
"""

como levanrtarlo:
  python register.py --tipo tipo_a
  python register.py --tipo tipo_b
  despues seleccionas el pais que quieras
  y te da las credenciales jej
"""

import argparse
import json
import os
import random
import string
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_URL = os.getenv("API_URL")
if not API_URL:
    print("Error: define API_URL en un archivo .env (ver .env.example)")
    sys.exit(1)

EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "example.com")
EMAIL_TAG = os.getenv("EMAIL_TAG", "testing")

COUNTER_FILE = Path(__file__).parent / "counter.json"

NOMBRES = [
    "Carlos", "María", "José", "Ana", "Luis", "Laura", "Miguel", "Sofía",
    "Andrés", "Valentina", "Ricardo", "Camila", "Fernando", "Isabella",
    "Jorge", "Daniela", "Roberto", "Mariana", "Eduardo", "Gabriela",
]
APELLIDOS = [
    "García", "Martínez", "López", "González", "Rodríguez", "Hernández",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
    "Díaz", "Cruz", "Morales", "Reyes", "Gutiérrez", "Ortiz", "Mendoza",
]
WEBSITES = [
    "https://www.ejemplo.com",
    "https://www.sitio-demo.mx",
    "https://www.pagina-test.co",
    "https://www.placeholder.lat",
]


def gen_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$"
    # si no le metes mayúscula+minúscula+número+símbolo a fuerza, la API te rebota
    pwd = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$"),
    ]
    pwd += [random.choice(chars) for _ in range(length - 4)]
    random.shuffle(pwd)
    return "".join(pwd)


def gen_phone():
    return "55" + "".join([str(random.randint(0, 9)) for _ in range(8)])


def read_counter():
    if not COUNTER_FILE.exists():
        return {"tipo_a": 0, "tipo_b": 0}
    with open(COUNTER_FILE) as f:
        return json.load(f)


def write_counter(counter):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter, f, indent=2)
        f.write("\n")


def fetch(endpoint):
    r = requests.get(f"{API_URL}{endpoint}")
    r.raise_for_status()
    return r.json()


def pick(lst):
    # cuando no hay resultados la API a veces regresa {} en vez
    # de []
    if not isinstance(lst, list) or not lst:
        return None
    return random.choice(lst)["id"]


def pick_str(lst):
    return random.choice(lst)


def elegir_pais(countries):
    print("\nPaíses disponibles:")
    for i, c in enumerate(countries, 1):
        print(f"  {i}. {c['name']}")
    while True:
        opcion = input("\n¿De qué país? (número): ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(countries):
            return countries[int(opcion) - 1]
        print(f"  Elige un número entre 1 y {len(countries)}")


def load_dropdowns(tipo):
    print("Cargando catálogos de la API...", end=" ", flush=True)
    countries = fetch("/countries?is_active=true")
    print("OK")
    country = elegir_pais(countries)
    country_id = country["id"]
    country_name = country["name"]
    print(f"País seleccionado: {country_name}")
    print("Cargando resto de catálogos...", end=" ", flush=True)

    states = fetch(f"/countries/name/{requests.utils.quote(country_name)}/states")
    intl_codes = fetch("/international-codes?is_active=true")
    # este endpoint viacio, no acepta filtro por country_id, así que
    # toca darle a mano comparando el nombre del país
    intl_code = next(
        (c for c in intl_codes if c["country_name"] == country_name),
        intl_codes[0],
    )

    currencies = fetch("/currencies")
    currency = next(
        (c for c in currencies if c["country_id"] == country_id),
        currencies[0],
    )

    data = {
        "country_id": country_id,
        "country_name": country_name,
        "state_id": pick(states) if states else None,
        "international_code_id": intl_code["id"],
        "currency_id": currency["id"],
    }

    # NOTA: los nombres de campos/endpoints de aquí para abajo son placeholders
    # (catalogo_1, catalogo_2, ...) — cámbialos por los catálogos reales de tu API
    if tipo == "tipo_a":
        data["catalogo_1_id"] = pick(fetch("/catalogo-1"))
        data["catalogo_2_id"] = pick(fetch("/catalogo-2"))
        data["catalogo_3_id"] = pick(fetch("/catalogo-3"))
        data["catalogo_4_id"] = pick(fetch("/catalogo-4"))
        data["catalogo_5_id"] = pick(fetch("/catalogo-5"))
        catalogo_6 = fetch(f"/catalogo-6?country_id={country_id}")
        if not catalogo_6:
            catalogo_6 = fetch("/catalogo-6")
        data["catalogo_6_id"] = pick(catalogo_6)

    if tipo == "tipo_b":
        data["catalogo_7_id"] = pick(fetch("/catalogo-7"))
        data["catalogo_8_id"] = pick(fetch("/catalogo-8"))
        catalogo_9 = fetch(f"/catalogo-9?country_id={country_id}")
        if not catalogo_9:
            catalogo_9 = fetch("/catalogo-9")
        data["catalogo_9_id"] = pick(catalogo_9)

    print("OK")
    return data


def register_usuario(tipo, numero, dropdowns):
    nombre = f"{pick_str(NOMBRES)} {pick_str(APELLIDOS)}"
    email = f"{tipo}+{EMAIL_TAG}+{numero}@{EMAIL_DOMAIN}"
    password = gen_password()

    payload = {
        "country_id": dropdowns["country_id"],
        "state_id": dropdowns["state_id"],
        "currency_id": dropdowns["currency_id"],
        "description_summary": f"Registro de prueba número {numero}.",
        "user": {
            "email": email,
            "password": password,
            "phone": gen_phone(),
            "name": nombre,
            "website": random.choice(WEBSITES),
            "international_code_id": dropdowns["international_code_id"],
            "legal_acceptances": True,
        },
    }

    if tipo == "tipo_a":
        payload["catalogo_1_id"] = dropdowns["catalogo_1_id"]
        payload["catalogo_2_id"] = dropdowns["catalogo_2_id"]
        payload["catalogo_3_id"] = dropdowns["catalogo_3_id"]
        payload["catalogo_4_id"] = dropdowns["catalogo_4_id"]
        payload["catalogo_5_id"] = dropdowns["catalogo_5_id"]
        payload["catalogo_6_id"] = dropdowns["catalogo_6_id"]
        endpoint = "/registro-tipo-a"
    else:
        payload["catalogo_7_id"] = dropdowns["catalogo_7_id"]
        payload["catalogo_8_id"] = dropdowns["catalogo_8_id"]
        payload["catalogo_9_id"] = dropdowns["catalogo_9_id"]
        endpoint = "/registro-tipo-b"

    print(f"Registrando {tipo} #{numero}...", end=" ", flush=True)
    r = requests.post(f"{API_URL}{endpoint}", json=payload)
    return r, email, password, payload


def main():
    parser = argparse.ArgumentParser(description="Registro automático de usuarios de prueba")
    parser.add_argument(
        "--tipo",
        choices=["tipo_a", "tipo_b"],
        required=True,
        help="Tipo de usuario a registrar",
    )
    args = parser.parse_args()
    tipo = args.tipo

    counter = read_counter()
    numero = counter[tipo] + 1

    try:
        dropdowns = load_dropdowns(tipo)
    except Exception as e:
        print(f"\nError al cargar catálogos: {e}")
        sys.exit(1)

    try:
        r, email, password, payload = register_usuario(tipo, numero, dropdowns)
    except Exception as e:
        print(f"\nError al hacer la petición: {e}")
        sys.exit(1)

    if r.status_code in (200, 201):
        print("OK")
        counter[tipo] = numero
        write_counter(counter)
        print()
        print("=" * 50)
        print(f"  Tipo:       {tipo}")
        print(f"  Número:     #{numero}")
        print(f"  Email:      {email}")
        print(f"  Password:   {password}")
        print(f"  País:       {dropdowns['country_name']}")
        print("=" * 50)
    else:
        print(f"FALLO ({r.status_code})")
        print()
        try:
            err = r.json()
            print("Respuesta de la API:")
            print(json.dumps(err, indent=2, ensure_ascii=False))
        except Exception:
            print(r.text)
        print()
        print("Payload enviado:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
