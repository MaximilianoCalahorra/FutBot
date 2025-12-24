# from telegram import Update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.api_service import ApiService
from utils.formatters import formatear_clasificacion_tabla, formatear_partidos, formatear_goleadores, formatear_equipo, formatear_entrenador, agrupar_plantel_por_posicion, formatear_grupo_plantel

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
            callback_data=f"equipo_seleccionar_{equipo['id']}"  # Callback con el id del equipo.
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
    
  async def equipo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Botón cliqueado.
    await query.answer()

    id_equipo = query.data.replace("equipo_seleccionar_", "")  # Obtener id del equipo.

    try:
      equipo = await self._api_service.obtener_equipo(id_equipo)  # Obtener equipo por su id.
      mensaje = formatear_equipo(equipo)  # Formatear mensaje con la información del equipo.
      
      # Botones de plantel y entrenador del equipo:
      botonera = [
        [
          InlineKeyboardButton(
            text="👥 Plantel",
            callback_data=f"equipo_plantel_{id_equipo}_0"
          ),
          InlineKeyboardButton(
            text="👔 Entrenador",
            callback_data=f"equipo_entrenador_{id_equipo}"
          )
        ]
      ]
      
      reply_markup = InlineKeyboardMarkup(botonera)

      await query.message.reply_html(
        mensaje,
        reply_markup=reply_markup)

    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo equipo: {e}")
  
  async def equipo_plantel_callback(self, update: Update, contenxt: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, _, id_equipo, index = query.data.split("_")
    index = int(index)

    plantel = await self._api_service.obtener_plantel(id_equipo)
    grupos = agrupar_plantel_por_posicion(plantel)
    
    if index < 0 or index >= len(grupos):
      await query.message.reply_text("❌ No hay más posiciones para mostrar.")
      return

    grupo, jugadores = grupos[index]
    texto = formatear_grupo_plantel(grupo, jugadores)

    botones = []

    if index > 0:
      botones.append(
        InlineKeyboardButton("⬅️", callback_data=f"equipo_plantel_{id_equipo}_{index-1}")
      )

    if index < len(grupos) - 1:
      botones.append(
        InlineKeyboardButton("➡️", callback_data=f"equipo_plantel_{id_equipo}_{index+1}")
      )

    reply_markup = InlineKeyboardMarkup([botones])

    await query.message.edit_text(texto, reply_markup=reply_markup, parse_mode="HTML")

  async def equipo_entrenador_callback(self, update: Update, contenxt: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    id_equipo = query.data.replace("equipo_entrenador_", "")
    
    try:
      entrenador = await self._api_service.obtener_entrenador(id_equipo)
      mensaje = formatear_entrenador(entrenador)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo entrenador: {e}")