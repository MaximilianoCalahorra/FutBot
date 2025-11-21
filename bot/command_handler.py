from telegram import Update
from telegram.ext import ContextTypes
from services.football_data_org_api_service import FootballDataOrgApiService
from utils.formatters import formatear_clasificacion_tabla, formatear_partidos

class CommandHandlerBot:
  """
    Contiene los manejadores de comandos del bot.
  """
  def __init__(self, config):
    """
    Inicializa el manejador de comandos.
    """
    self._config = config
    self._api_service = FootballDataOrgApiService(config)
  
  async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /start.
    """
    user = update.effective_user
    await update.message.reply_html(
      f"¡Hola {user.mention_html()}! 👋 Soy <b>FutBot</b>, tu asistente especializado en fútbol ⚽.\n\n"
      "Puedo informarte sobre:\n"
      "📅 <b>Partidos del día</b>\n"
      "📊 <b>Tabla de posiciones</b>\n"
      "🥅 <b>Goleadores</b> y <b>asistidores</b>\n"
      "🟥 <b>Tarjetas</b> amarillas y rojas\n\n"
      "Escribí /ayuda para ver todos los comandos disponibles ⚙️"
    )

  async def ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /ayuda.
    """
    await update.message.reply_html(
      "📖 <b>Comandos disponibles</b>\n\n"
      "🤖 <b>/start</b> — Te da la bienvenida y explica qué puede hacer FutBot.\n"
      "📅 <b>/hoy</b> — Muestra los <b>partidos del día</b> (con hora y equipos).\n"
      "📊 <b>/tabla</b> — Muestra la <b>tabla de posiciones</b> actualizada.\n"
      "📈 <b>/estadisticas</b> — Muestra <b>goleadores</b>, <b>asistidores</b> y <b>sanciones</b> (amarillas y rojas).\n\n"
      "⚙️ Próximamente agregaré más funciones, como consultar equipos o jugadores específicos 👀"
    )

  async def hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /hoy.
    """
    try:
      partidos = await self._api_service.obtener_partidos_hoy()
      mensaje = formatear_partidos(partidos)
      await update.message.reply_html(mensaje)
    except Exception as e:
      await update.message.reply_text(f"❌ Error obteniendo los partidos de hoy: {e}")

  async def tabla(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /tabla.
    """
    try:
      clasificacion = await self._api_service.obtener_clasificacion()
      mensaje = formatear_clasificacion_tabla(clasificacion)
      await update.message.reply_html(mensaje)
    except Exception as e:
      await update.message.reply_text(f"❌ Error obteniendo la tabla: {e}")
    
  async def estadisticas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /estadisticas.
    """
    await update.message.reply_html(
      f"📈 <b>Estadísticas - 12/11/2025</b>\n\n"
        
      "🥅 <b>Goleadores</b>\n"
      "1️⃣ Pablo Vegetti (Belgrano) — 12 goles\n"
      "2️⃣ Miguel Borja (River) — 11 goles\n"
      "3️⃣ Edinson Cavani (Boca) — 10 goles\n"
      "4️⃣ Adrián Martínez (Racing) — 9 goles\n"
      "5️⃣ Franco Cristaldo (Lanús) — 8 goles\n\n"
      
      "🎯 <b>Asistidores</b>\n"
      "1️⃣ Cristian Ferreira (Talleres) — 8 asistencias\n"
      "2️⃣ Ezequiel Barco (River) — 7 asistencias\n"
      "3️⃣ Valentín Barco (Boca) — 6 asistencias\n"
      "4️⃣ Ignacio Malcorra (Central) — 5 asistencias\n"
      "5️⃣ Maxi Meza (Estudiantes) — 5 asistencias\n\n"
      
      "🟨 <b>Tarjetas Amarillas</b>\n"
      "1️⃣ Rodrigo Aliendro (River) — 6\n"
      "2️⃣ Damián Pérez (Arsenal) — 5\n"
      "3️⃣ Gastón Benavídez (Talleres) — 5\n"
      "4️⃣ Nicolás Oroz (Racing) — 4\n"
      "5️⃣ Enzo Díaz (River) — 4\n\n"
      
      "🟥 <b>Tarjetas Rojas</b>\n"
      "1️⃣ Marcos Rojo (Boca) — 2\n"
      "2️⃣ Carlos Quintana (Lanús) — 2\n"
      "3️⃣ Gabriel Hauche (Racing) — 1\n"
      "4️⃣ Enzo Pérez (Estudiantes) — 1\n"
      "5️⃣ Jonathan Galván (Huracán) — 1"
    )