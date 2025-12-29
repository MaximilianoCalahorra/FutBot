# ⚽ FutBot — La Liga (España)

Asistente de Telegram que brinda información actualizada sobre La Liga de España 🇪🇸:
partidos del día, tabla de posiciones, top 10 de goleadores e información sobre los equipos.

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
│   ├── futbot.py               # Inicializa el bot, registra comandos y callbacks
│   └── command_handler.py      # Implementación de cada comando
│
├── services/
│   └── api_service.py          # Capa de comunicación con APIs externas (Football-Data + SoccerData)
│
└── utils/
    └── formatters.py           # Funciones reutilizables para formatear mensajes
```

---

## ⚙️ Comandos implementados

| Comando       | Descripción                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| `/start`      | Da la bienvenida y explica las funciones del bot.                           |
| `/ayuda`      | Lista todos los comandos disponibles.                                       |
| `/hoy`        | Muestra los partidos del día en La Liga.                                    |
| `/tabla`      | Muestra la tabla de posiciones actualizada.                                 |
| `/goleadores` | Muestra el top 10 de máximos goleadores del campeonato.                     |
| `/equipo`     | Permite explorar información detallada de un equipo mediante botoneras.    |

---

### 👋 Comando `/start`

El comando `/start` da la bienvenida al usuario e introduce las funcionalidades principales del bot.

🔹 **Flujo de uso**

1. El usuario ejecuta el comando: `/start`

2. El bot responde con:

    - Un mensaje de bienvenida.

    - Una breve explicación de qué información puede brindar.

    - Una invitación a usar `/ayuda` para ver el listado completo de comandos.

Este comando está pensado como **punto de entrada** para nuevos usuarios.

---

### ℹ️ Comando `/ayuda`

El comando `/ayuda` muestra un resumen claro de todos los comandos disponibles en el bot.

🔹 **Flujo de uso**

1. El usuario ejecuta el comando: `/ayuda`

2. El bot responde con:

    - Una lista de comandos.

    - Una breve descripción de qué hace cada uno.

Sirve como **guía rápida** para recordar las funcionalidades del bot.

---

### 📅 Comando `/hoy`

El comando `/hoy` muestra los partidos de La Liga correspondientes al día actual.

🔹 **Flujo de uso**

1. El usuario ejecuta el comando: `/hoy`

2. El bot permite seleccionar al usuario el estado de los partidos que quiere consultar, siendo las opciones: programados, en juego o finalizados.

3. El bot obtiene los partidos del día que se encuentren en el estado indicado desde la API.

4. Para cada partido, el bot muestra información según su estado:

    - 🕒 **Partido a futuro**: fecha, hora y equipos.

    - ⏳ **Partido en juego**: marcador actual y eventos.

    - 🏁 **Partido finalizado**: resultado final y eventos destacados.

5. En partidos en juego o finalizados, se incluyen eventos como:

    - ⚽️ Gol

    - ⚽️(P) Gol de penal

    - ⚽️(EC) Gol en contra

    - 🔄 Cambios

    - 🟥 Tarjetas rojas

    - 🟨 Tarjetas amarillas

El formato se adapta dinámicamente según el estado del partido.

---

### 🏆 Comando `/tabla`

El comando `/tabla` muestra la tabla de posiciones actualizada de La Liga.

🔹 **Flujo de uso**

1. El usuario ejecuta el comando: `/tabla`

2. El bot consulta la API de Football-Data.

3. Se muestra una tabla con:

    - Posición

    - Equipo

    - Partidos jugados

    - Diferencia de gol

    - Puntos

    - Estado de clasificación a copas europeas.

La información se presenta de forma compacta y fácil de leer dentro del chat.

---

### ⚽ Comando `/goleadores`

El comando `/goleadores` muestra el ranking de los máximos goleadores del campeonato.

🔹 **Flujo de uso**

1. El usuario ejecuta el comando: `/goleadores`

2. El bot obtiene el ranking desde la API.

3. Se muestra el **top 10 de goleadores**, incluyendo:

    - Posición en el ranking

    - Nombre del jugador

    - Equipo

    - Cantidad de goles

Este comando permite tener una vista rápida del rendimiento ofensivo de la liga.

---

### 🛡️ Comando `/equipo`

El comando `/equipo` permite al usuario explorar información detallada de los clubes de La Liga
de forma interactiva mediante **botoneras y navegación por callbacks**.

#### 🔹 Flujo de uso

1. El usuario ejecuta el comando: `/equipo`

2. El bot muestra una lista de equipos mediante botones inline.

3. Al seleccionar un equipo, se muestra un mensaje con información general del club:
    - Nombre

    - Estadio y dirección

    - Año de fundación

    - Sitio web

    - Entrenador

    - Cantidad de jugadores registrados

4. Debajo del mensaje, se presentan botones adicionales para profundizar:
    - 👥 Plantel

    - 👔 Entrenador

    - ⚡ Racha

    - 🗓️ Próximos partidos

---

### 👥 Plantel

- Muestra la plantilla del equipo agrupada por posiciones:
    - 🧤 Arqueros

    - 🛡️ Defensores

    - ⚙️ Mediocampistas

    - 🎯 Delanteros

- Cada grupo se navega mediante paginación con botones ⬅️ ➡️.

- La información se actualiza editando el mismo mensaje, evitando spam en el chat.

- Cada jugador incluye:

    - Nombre

    - Posición

    - Fecha de nacimiento (formato dd-mm-yyyy)

    - Nacionalidad representada con bandera cuando es posible, o nombre del país como fallback.

---

### 👔 Entrenador

Muestra información específica del entrenador del equipo:

- Nombre

- Fecha de nacimiento

- Nacionalidad (con bandera o nombre)

- Duración del contrato

---

### ⚡ Racha

Muestra información sobre los últimos 5 encuentros que disputó el equipo en la competencia:

- Resultado del partido

- Fecha

- Número de jornada

- Situación de localía

- Equipos que disputaron el encuentro

---

### 🗓️ Próximos partidos

Muestra información sobre los próximos 5 encuentros que el equipo debe disputar en la competencia:

- Situación de localía

- Fecha y hora

- Número de jornada

- Equipos que participarán del encuentro

---

## 🌐 APIs utilizadas

El bot combina información obtenida desde dos APIs para cubrir todos los datos necesarios:

### 1️⃣ Football-Data API (v4)

https://api.football-data.org/v4/

Usada para:
- Tabla de posiciones.
- Ranking de goleadores.
- Información sobre los equipos.

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

- Equipos

Esto permite que el resto del código no dependa de detalles HTTP.

---

🔹 **`formatters.py`**

Conjunto de funciones responsables de dar forma a los mensajes enviados al usuario:

- Formateo de partidos según estado: 🕒 futuros — ⏳ en juego — 🏁 finalizados

- Formato de eventos del partido (incluye íconos como ⚽️, ⚽️(P), 🔄, 🟥, etc.)

- Tabla de posiciones

- Ranking de goleadores

- Jugador

- Entrenador

- Plantel completo

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
pycountry==24.6.1
```

| Paquete               | Uso                                         |
| --------------------- | ------------------------------------------- |
| `python-telegram-bot` | Manejo de la API de Telegram en modo async. |
| `aiohttp`             | Requests asincrónicos a las APIs.           |
| `python-dotenv`       | Carga de variables desde `.env`.            |
| `pycountry` | Resolución de países y códigos ISO para banderas |

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