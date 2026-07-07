# api-register-scripts

Scripts de automatización para registro de usuarios en una plataforma.

## Requisitos

- Python 3.9+
- pip

## Instalación

```bash
pip install requests python-dotenv
```

## Configuración

Copia el archivo de ejemplo y complétalo con la URL de tu ambiente:

```bash
cp .env.example .env
```

Edita `.env`:

```
API_URL=https://tu-api-aqui.com
EMAIL_DOMAIN=tu-dominio.com
EMAIL_TAG=testing
```

`EMAIL_DOMAIN` y `EMAIL_TAG` son opcionales (usan `example.com` y `testing` por default) y sirven para generar los correos de prueba con el truco de `+alias` de Gmail-style addressing.

## Uso

```bash
# Registrar un comprador
python register.py --tipo comprador

# Registrar un vendedor
python register.py --tipo vendedor
```

Cada ejecución genera un usuario con email único y contraseña aleatoria. Al terminar imprime las credenciales para que puedas hacer login.

Los contadores se guardan localmente en `counter.json` (no se sube al repo).
