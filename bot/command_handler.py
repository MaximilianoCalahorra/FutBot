# from telegram import Update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.api_service import ApiService
from utils.formatters import formatear_clasificacion_tabla, formatear_partidos, formatear_goleadores, formatear_equipo

class CommandHandlerBot:
  """
    Contiene los manejadores de comandos del bot.
  """
  def __init__(self, config):
    """
    Inicializa el manejador de comandos.
    """
    self._config = config
    self._api_service = ApiService(config)
  
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
      "🥅 <b>Goleadores</b>\n\n"
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
      "📈 <b>/goleadores</b> — Muestra el <b>top 10</b> de goleadores.\n\n"
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
    
  async def goleadores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /goleadores.
    """
    try:
      goleadores = await self._api_service.obtener_goleadores()
      mensaje = formatear_goleadores(goleadores)
      await update.message.reply_html(mensaje)
    except Exception as e:
      await update.message.reply_text(f" Error obteniendo los goleadores: {e}")
  
  async def equipos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /equipos
    """
    try:
      # Listado de equipos:
      equipos = await self._api_service.obtener_equipos()

      # Armado de la botonera:
      botonera = []  # Botonera final con el listado de filas.
      fila = []  # Listado de elementos por fila.

      # Recorrer equipos:
      for i, equipo in enumerate(equipos, start=1):
        # Agrega un equipo a la fila:
        fila.append(
          InlineKeyboardButton(
            text=equipo["nombre"],  # Nombre del equipo.
            callback_data=f"equipo_{equipo['id']}"  # Callback con el id del equipo.
          )
        )

        # Genera hasta 2 botones por fila:
        if i % 2 == 0:
          botonera.append(fila)
          fila = []

      # Fila extra si la cantidad de equipos es impar:
      if fila:
        botonera.append(fila)

      reply_markup = InlineKeyboardMarkup(botonera)  # Botonera en formato aceptado por Telegram.

      await update.message.reply_text(
        "🛡️ Seleccioná un equipo:",
        reply_markup=reply_markup
      )

    except Exception as e:
      await update.message.reply_text(f"❌ Error cargando equipos: {e}")
    
  async def equipos_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Botón cliqueado.
    await query.answer()

    id_equipo = query.data.replace("equipo_", "")  # Obtener id del equipo.

    try:
      equipo = await self._api_service.obtener_equipo(id_equipo)  # Obtener equipo por su id.
      mensaje = formatear_equipo(equipo)  # Formatear mensaje con la información del equipo.

      await query.message.reply_html(mensaje)

    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo equipo: {e}")