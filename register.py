#este es un script hechjo para dejar de llenar forms enormes jaja just for fun
"""

como levanrtarlo:
  python register.py --tipo comprador
  python register.py --tipo vendedor
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
EMPRESAS = [
    "Soluciones", "Tecnología", "Grupo", "Servicios", "Inversiones",
    "Comercial", "Industrial", "Digital", "Capital", "Estrategia",
]
SUFIJOS_EMPRESA = [
    "MX", "LATAM", "Global", "Partners", "Corp", "SA", "Holdings",
]
WEBSITES = [
    "https://www.ejemplo.com",
    "https://www.miempresa.mx",
    "https://www.negocio.co",
    "https://www.corporativo.lat",
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
        return {"comprador": 0, "vendedor": 0}
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

    if tipo == "vendedor":
        data["industry_id"] = pick(fetch("/industries"))
        data["company_type_id"] = pick(fetch("/company_types"))
        data["interest_id"] = pick(fetch("/interests"))
        data["user_company_role_id"] = pick(fetch("/user_company_roles"))
        data["ebitda_range_id"] = pick(fetch("/ebitda_ranges"))
        yearly_sales = fetch(f"/yearly_sales_ranges?country_id={country_id}")
        if not yearly_sales:
            yearly_sales = fetch("/yearly_sales_ranges")
        data["yearly_sales_range_id"] = pick(yearly_sales)

    if tipo == "comprador":
        data["buyer_description_id"] = pick(fetch("/buyer_descriptions"))
        data["transaction_experience_id"] = pick(fetch("/transaction_experiences"))
        investment_sizes = fetch(f"/investment_sizes?country_id={country_id}")
        if not investment_sizes:
            investment_sizes = fetch("/investment_sizes")
        data["investment_size_id"] = pick(investment_sizes)

    print("OK")
    return data


def register_vendedor(numero, dropdowns):
    nombre = f"{pick_str(NOMBRES)} {pick_str(APELLIDOS)}"
    empresa = f"{pick_str(EMPRESAS)} {pick_str(APELLIDOS)} {pick_str(SUFIJOS_EMPRESA)}"
    email = f"vendedor+{EMAIL_TAG}+{numero}@{EMAIL_DOMAIN}"
    password = gen_password()

    # le puse este rango pa que no salgan empresas "recién nacidas" ni unas
    # ya jubiladas del siglo pasado, así se ve más creíble el dato
    year = random.randint(2000, 2020)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    foundation_date = f"{year}-{month}-{day}"

    headcount = random.choice([5, 10, 25, 50, 100, 200, 500])

    payload = {
        "user": {
            "email": email,
            "password": password,
            "phone": gen_phone(),
            "name": nombre,
            "international_code_id": dropdowns["international_code_id"],
            "legal_acceptances": True,
        },
        "name": empresa,
        "website": random.choice(WEBSITES),
        "foundation_date": foundation_date,
        "headcount": headcount,
        "short_description": f"Empresa de prueba número {numero} registrada automáticamente.",
        "industry_id": dropdowns["industry_id"],
        "company_type_id": dropdowns["company_type_id"],
        "country_id": dropdowns["country_id"],
        "state_id": dropdowns["state_id"],
        "interest_id": dropdowns["interest_id"],
        "user_company_role_id": dropdowns["user_company_role_id"],
        "ebitda_range_id": dropdowns["ebitda_range_id"],
        "yearly_sales_range_id": dropdowns["yearly_sales_range_id"],
        "currency_id": dropdowns["currency_id"],
    }
 
    print(f"Registrando vendedor #{numero}...", end=" ", flush=True)
    r = requests.post(f"{API_URL}/sellers", json=payload)
    return r, email, password, payload


def register_comprador(numero, dropdowns):
    nombre = f"{pick_str(NOMBRES)} {pick_str(APELLIDOS)}"
    email = f"comprador+{EMAIL_TAG}+{numero}@{EMAIL_DOMAIN}"
    password = gen_password()

    payload = {
        "buyer_description_id": dropdowns["buyer_description_id"],
        "country_id": dropdowns["country_id"],
        "state_id": dropdowns["state_id"],
        "investment_description_summary": f"Inversionista de prueba número {numero}. Buscando oportunidades en LATAM.",
        "investment_size_id": dropdowns["investment_size_id"],
        "currency_id": dropdowns["currency_id"],
        "transaction_experience_id": dropdowns["transaction_experience_id"],
        "user": {
            "email": email,
            "password": password,
            "phone": gen_phone(),
            "name": nombre,
            "website": random.choice(WEBSITES),
            "legal_acceptances": True,
        },
    }

    print(f"Registrando comprador #{numero}...", end=" ", flush=True)
    r = requests.post(f"{API_URL}/buyers", json=payload)
    return r, email, password, payload


def main():
    parser = argparse.ArgumentParser(description="Registro automático de usuarios de prueba")
    parser.add_argument(
        "--tipo",
        choices=["comprador", "vendedor"],
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
        if tipo == "vendedor":
            r, email, password, payload = register_vendedor(numero, dropdowns)
        else:
            r, email, password, payload = register_comprador(numero, dropdowns)
    except Exception as e:
        print(f"\nError al hacer la petición: {e}")
        sys.exit(1)

    if r.status_code in (200, 201):
        print("OK")
        counter[tipo] = numero
        write_counter(counter)
        print()
        print("=" * 50)
        print(f"  Tipo:       {tipo.capitalize()}")
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
