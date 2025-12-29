# from telegram import Update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.api_service import ApiService
from utils.formatters import formatear_clasificacion_tabla, formatear_partido, formatear_goleadores, formatear_equipo, formatear_entrenador, agrupar_plantel_por_posicion, formatear_grupo_plantel, formatear_racha, formatear_proximos_partidos

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
      "🥅 <b>Goleadores</b>\n"
      "🛡️ <b>Equipos</b>\n\n"
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
      "📈 <b>/goleadores</b> — Muestra el <b>top 10</b> de goleadores.\n"
      "🛡️ <b>/equipos</b> — Muestra información general del club y permite acceder a mayor detalle sobre el plantel y el entrenador mediante botones.\n\n"
    )

  async def hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /hoy.
    """
    try:
      # Armado de la botonera:
      botonera = []
      textos = ["🕒 Programados", "⏳ En juego", "🏁 Finalizados"]
      callbacks = ["hoy_partidos_pre-match_0", "hoy_partidos_live_0", "hoy_partidos_finished_0"]
      
      for i in range(len(textos)):
        botonera.append([
          InlineKeyboardButton(
            text=textos[i],
            callback_data=callbacks[i]
          )
        ])
      
      reply_markup = InlineKeyboardMarkup(botonera)
      
      await update.message.reply_text(
        "⚽ Seleccioná un estado de los partidos:",
        reply_markup=reply_markup
      )
      
    except Exception as e:
      await update.message.reply_text(f"❌ Error obteniendo los partidos de hoy: {e}")

  async def hoy_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Botón cliqueado.
    await query.answer()
    
    _, _, estado_partido, index = query.data.split("_")  # Obtener estado de los partidos solicitado y página de partido.
    index = int(index)
    
    partidos = await self._api_service.obtener_partidos_hoy(estado_partido)  # Partidos en ese estado.
    
    # Si no hay partidos:
    if len(partidos) == 0:
      await query.message.reply_text("❌ No hay partidos para mostrar.")
      return
    
    if index < 0 or index >= len(partidos):
      await query.message.reply_text("❌ No hay más partidos para mostrar.")
      return
      
    texto = formatear_partido(partidos[index])  # Formateado del partido de la página actual.
    
    # Botonera para avanzar/retroceder a través de las páginas:
    botones = []
    
    if index > 0:
      botones.append(
        InlineKeyboardButton("⬅️", callback_data=f"hoy_partidos_{estado_partido}_{index - 1}")
      )
    
    if index < len(partidos) - 1:
      botones.append(
        InlineKeyboardButton("➡️", callback_data=f"hoy_partidos_{estado_partido}_{index + 1}")
      )
    
    reply_markup = InlineKeyboardMarkup([botones])
    
    hoy_partidos_msg_id = context.user_data.get("hoy_partidos_message_id")
    
    # Si todavía no hubo un mensaje sobre los partidos:
    if hoy_partidos_msg_id is None:
      sent = await query.message.reply_html(
        texto,
        reply_markup=reply_markup
      )
      context.user_data["hoy_partidos_message_id"] = sent.message_id  # Generamos un nuevo mensaje con el contenido.
    else: # Si ya hubo al menos un mensaje:
      # Editamos el mensaje con el nuevo contenido:
      await context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=hoy_partidos_msg_id,
        text=texto,
        reply_markup=reply_markup,
        parse_mode="HTML"
      )
  
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
        ],
        [
          InlineKeyboardButton(
            text="⚡ Racha",
            callback_data=f"equipo_racha_{id_equipo}"
          ),
          InlineKeyboardButton(
            text="🗓️ Próximos partidos",
            callback_data=f"equipo_proximos_partidos_{id_equipo}"
          )
        ]
      ]
      
      reply_markup = InlineKeyboardMarkup(botonera)

      await query.message.reply_html(
        mensaje,
        reply_markup=reply_markup)

    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo equipo: {e}")
  
  async def equipo_plantel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    plantel_msg_id = context.user_data.get("plantel_message_id")

    # Si todavía no hubo un mensaje sobre el plantel:
    if plantel_msg_id is None:
      sent = await query.message.reply_html(
        texto,
        reply_markup=reply_markup
      )
      context.user_data["plantel_message_id"] = sent.message_id  # Generamos un nuevo mensaje con el contenido.
    else:  # Si ya hubo al menos un mensaje:
      # Editamos el mensaje con el nuevo contenido:
      await context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=plantel_msg_id,
        text=texto,
        reply_markup=reply_markup,
        parse_mode="HTML"
      )

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
      
  async def equipo_racha_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    id_equipo = query.data.replace("equipo_racha_", "")
    
    try:
      racha = await self._api_service.obtener_racha(id_equipo)
      mensaje = formatear_racha(racha, id_equipo)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo racha: {e}")
      
  async def equipo_proximos_partidos_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    id_equipo = query.data.replace("equipo_proximos_partidos_", "")
    
    try:
      proximos_partidos = await self._api_service.obtener_proximos_partidos(id_equipo)
      mensaje = formatear_proximos_partidos(proximos_partidos, id_equipo)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo próximos partidos: {e}")