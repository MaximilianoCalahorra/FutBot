# ⚽ FutBot — La Liga (España)

Asistente de Telegram que brinda información actualizada sobre La Liga de España 🇪🇸:
partidos del día, tabla de posiciones y top 10 de goleadores.

## 🏗️ Estructura actual del proyecto

```bash
futbot/
├── main.py                     # Punto de entrada del bot
├── .env                        # Variables sensibles
├── .env.example                # Ejemplo de configuración
│
├── config/
│   └── config.py               # Clase Config: carga variables de entorno y constantes del proyecto
│
├── bot/
│   ├── futbot.py               # Inicializa el bot, registra comandos y arranca la app
│   └── command_handler.py      # Implementación de cada comando (/start, /ayuda, /hoy, /tabla, /goleadores)
│
├── services/
│   └── api_service.py          # Capa de comunicación con APIs externas (Football-Data + SoccerData)
│
└── utils/
    └── formatters.py           # Funciones reutilizables para formatear mensajes (partidos, tabla, goles, eventos)
```

---

## ⚙️ Comandos implementados

| Comando       | Descripción                                             |
| ------------- | ------------------------------------------------------- |
| `/start`      | Da la bienvenida y explica las funciones del bot.       |
| `/ayuda`      | Lista todos los comandos disponibles.                   |
| `/hoy`        | Muestra los partidos del día en La Liga.                |
| `/tabla`      | Muestra la tabla de posiciones actualizada.             |
| `/goleadores` | Muestra el top 10 de máximos goleadores del campeonato. |

---

## 🌐 APIs utilizadas

El bot combina información obtenida desde dos APIs para cubrir todos los datos necesarios:

### 1️⃣ Football-Data API (v4)

https://api.football-data.org/v4/

Usada para:
- Tabla de posiciones.
- Ranking de goleadores.

### 2️⃣ SoccerData API

https://api.soccerdataapi.com/

Usada para:
- Partidos del día con los eventos en caso de que sea un partido en juego o finalizado.

---

## ⚙️ Configuración con .env

El archivo `.env` debe incluir las siguientes variables:

```bash
TELEGRAM_TOKEN=tu_token_de_telegram
FOOTBALL_DATA_ORG_API_KEY=tu_api_key_de_football_data_org
SOCCERDATA_API_KEY=tu_api_key_de_soccerdata
```

📄 En el repositorio hay un `.env.example` para guiar la configuración inicial.

---

## 🧠 Descripción técnica

🔹 **`Config`**

- Carga las variables de entorno mediante `python-dotenv`.

- Expone claves de APIs y parámetros de configuración generales.

- Define constantes como:

    - id de La Liga para ambas APIs

    - Zona horaria y formatos de fecha

    - URLs base de cada API

Incluye validaciones para asegurar que el bot no se ejecute con claves ausentes.

---

🔹 **`ApiService`**

Capa intermedia encargada de interactuar con las APIs externas.

Encapsula peticiones como:

- Partidos del día y sus eventos

- Tabla completa

- Goleadores

Esto permite que el resto del código no dependa de detalles HTTP.

---

🔹 **`formatters.py`**

Conjunto de funciones responsables de dar forma a los mensajes enviados al usuario:

- Formateo de partidos según estado: 🕒 futuros — ⏳ en juego — 🏁 finalizados

- Formato de eventos del partido (incluye íconos como ⚽️, ⚽️(P), 🔄, 🟥, etc.)

- Tabla de posiciones

- Ranking de goleadores

Separar esta lógica permite mantener el bot modular y escalable.

---

🔹 **`FutBot`** y **`CommandHandler`**

- Registran los comandos del bot.

- Implementan el flujo de respuesta para cada comando.

- Llaman a `ApiService` para obtener datos.

- Delegan en `formatters.py` para dar estructura a los mensajes.

El bot se ejecuta con:

```bash
application.run_polling()
```
---

## 📦 Dependencias (`requirements.txt`)

```txt
python-telegram-bot==21.4
aiohttp==3.9.5
python-dotenv==1.0.1
```

| Paquete               | Uso                                         |
| --------------------- | ------------------------------------------- |
| `python-telegram-bot` | Manejo de la API de Telegram en modo async. |
| `aiohttp`             | Requests asincrónicos a las APIs.           |
| `python-dotenv`       | Carga de variables desde `.env`.            |

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