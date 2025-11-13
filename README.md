# ⚽ FutBot — Liga Profesional Argentina

Asistente de Telegram que brinda información sobre la Liga Profesional Argentina 🇦🇷: partidos del día, tabla de posiciones y estadísticas de jugadores (goleadores, asistidores y sanciones).

## 🏗️ Estructura actual del proyecto

```bash
futbot/
├── main.py                   # Punto de entrada del bot
├── .env                      # Variables sensibles (token y API key)
├── .env.example              # Ejemplo de variables requeridas
├── config/
│   └── config.py             # Clase Config: carga de .env y parámetros del proyecto
└── services/
    ├── futbot.py             # Clase principal FutBot (configura y ejecuta el bot)
    └── command_handler.py    # Maneja comandos /start, /ayuda, /hoy, /tabla, /estadisticas
```

---

## ⚙️ Comandos implementados

| Comando         | Descripción                                                    |
| --------------- | -------------------------------------------------------------- |
| `/start`        | Da la bienvenida y explica las funciones del bot.              |
| `/ayuda`        | Lista todos los comandos disponibles.                          |
| `/hoy`          | Muestra los partidos del día en la Liga Profesional Argentina. |
| `/tabla`        | Muestra la tabla de posiciones actualizada.                    |
| `/estadisticas` | Muestra los goleadores, asistidores y sanciones.               |

(*Actualmente las respuestas son simuladas; en la próxima etapa se conectarán con la API real.*)

---

## ⚙️ Configuración con .env

El archivo `.env` debe incluir las siguientes variables:

```bash
TELEGRAM_TOKEN=tu_token_de_telegram
FOOTBALL_API_KEY=tu_api_key_de_football
```

📄 En el repositorio hay un `.env.example` para guiar la configuración inicial.

---

## 🧠 Descripción técnica

🔹 **Clase `Config`**

- Carga las variables de entorno automáticamente (`load_dotenv()`).

- Expone propiedades para acceder a `TELEGRAM_TOKEN`, `FOOTBALL_API_KEY`, y parámetros fijos como:

  - `id_liga = 128` (Liga Profesional Argentina)

  - `temporada = 2025`

  - `football_api_base_url = "https://v3.football.api-sports.io/"`

Incluye validaciones para asegurar que el entorno esté correctamente configurado antes de iniciar el bot.

---

🔹 **Clase `FutBot`**

- Crea la aplicación principal de Telegram usando `Application.builder()`.

- Registra los comandos disponibles mediante `CommandHandler`.

- Inicia el bot con `run_polling()`.

---

🔹 **Clase `CommandHandlerBot`**

Maneja cada comando de usuario.

Actualmente las respuestas son estáticas, pero respetan el formato y los estilos (HTML con emojis y estructura limpia).

Ejemplo de `/start`:

```text
¡Hola Maxi! 👋 Soy FutBot, tu asistente especializado en fútbol ⚽."

Puedo informarte sobre:
📅 Partidos del día
📊 Tabla de posiciones
🥅 Goleadores y asistidores
🟥 Tarjetas amarillas y rojas

Escribí /ayuda para ver todos los comandos disponibles ⚙️
```

---

## 📦 Dependencias (`requirements.txt`)

```txt
python-telegram-bot==21.4
requests==2.32.3
python-dotenv==1.0.1
```

| Paquete               | Uso                                    | Comentario                                                       |
| --------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| `python-telegram-bot` | Manejo de la API de Telegram.          | Versión 21+ con soporte async y tipado moderno. |
| `requests`            | Consultas HTTP a la API-Football.      | Ligero y confiable.                |
| `python-dotenv`       | Carga de variables del archivo `.env`. | Facilita la configuración.                          |

---

## 💡 Ejecución local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
# (completar con tus claves)

# Ejecutar el bot
python main.py
```