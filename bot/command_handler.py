from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date, timedelta
from utils.formatters import formatear_clasificacion_tabla, formatear_partido, formatear_goleadores, formatear_equipo, formatear_entrenador, agrupar_plantel_por_posicion, formatear_grupo_plantel, formatear_racha, formatear_proximos_partidos, formatear_previa_partido, formatear_partidos_historial
from bot.keyboards import teclado_partido

class CommandHandlerBot:
  """
    Contiene los manejadores de comandos del bot.
  """
  def __init__(self, api_service):
    """
    Inicializa el manejador de comandos.
    """
    self._api_service = api_service
  
  async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /start.
    """
    user = update.effective_user
    await update.message.reply_html(
      f"¡Hola {user.mention_html()}! 👋 Soy <b>FutBot</b>, tu asistente especializado en fútbol ⚽.\n\n"
      "Puedo informarte sobre:\n"
      "📅 <b>Partidos del día y del siguiente</b>\n"
      "📊 <b>Tabla de posiciones</b>\n"
      "🥅 <b>Goleadores</b>\n"
      "🛡️ <b>Equipos</b>\n"
      "📅 <b>Partidos de una jornada</b>\n\n"
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
      "📅 <b>/maniana</b> — Muestra los <b>partidos del día siguiente</b> (con hora y equipos).\n"
      "📊 <b>/tabla</b> — Muestra la <b>tabla de posiciones</b> actualizada.\n"
      "📈 <b>/goleadores</b> — Muestra el <b>top 10</b> de goleadores.\n"
      "🛡️ <b>/equipos</b> — Muestra información general del club y permite acceder a mayor detalle sobre el plantel, el entrenador, racha del equipo y próximos encuentros mediante botones.\n"
      "📅 <b>/jornada &lt;número&gt;</b> — Muestra información sobre todos los partidos de la jornada solicitada.\n\n"
    )

  async def hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /hoy.
    """
    try:
      # Armado de la botonera:
      botonera = []
      textos = ["🕒 Programados", "⏳ En juego", "🏁 Finalizados", "📅 ➡️ ⚽ Pospuestos"]
      callbacks = ["hoy_partidos_pre-match_0", "hoy_partidos_live_0", "hoy_partidos_finished_0", "hoy_partidos_postponed_0"]
      
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
    query = update.callback_query
    await query.answer("⏳ Cargando partidos…")

    _, _, estado, _ = query.data.split("_")  # Obtener estado de los partidos solicitados.

    hoy = date.today().strftime("%d-%m-%Y")  # Fecha de hoy.
    partidos = await self._api_service.obtener_partidos_estado_y_fecha(estado, hoy)

    if not partidos:
      await query.message.reply_text("❌ No hay partidos para mostrar.")
      return

    # Carga de valores útiles:
    scope = "hoy"
    index = 0

    context.user_data["hoy_estado"] = estado
    context.user_data["hoy_partidos"] = partidos
    context.user_data["hoy_index"] = index
    context.user_data["scope_actual"] = scope

    texto = formatear_partido(partidos[index])

    # Construcción del teclado que acompaña a cada partido:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=(partidos[index]["estado"] == "pre-match"),  # Solo si es un partido programado ofrece la posibilidad de consultar la previa.
      id_partido=partidos[index].get("id")  # Id del partido a mostrar.
    )

    sent = await query.message.reply_html(texto, reply_markup=reply_markup)
    context.user_data[f"{scope}_message_id"] = sent.message_id
    
  async def navegar_partido_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Permite desplazarse entre partidos.
    """
    query = update.callback_query
    await query.answer("⏳ Cargando partido…")

    _, scope, index = query.data.split("_")  # Obtener entorno desde el que se llamó y partido solicitado.
    index = int(index)

    partidos = context.user_data.get(f"{scope}_partidos")  # Partidos correspondientes a ese entorno.
    msg_id = context.user_data.get(f"{scope}_message_id")  # Id del mensaje.

    if not partidos:
      await query.message.reply_text("❌ La sesión expiró.")
      return

    # Cargar los nuevos valores para el entorno y el partido solicitado:
    context.user_data[f"{scope}_index"] = index
    context.user_data["scope_actual"] = scope

    # Acceder al partido solicitado y formatearlo:
    partido = partidos[index]
    texto = formatear_partido(partido)

    # Construcción del teclado que acompaña al partido:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=(partido["estado"] == "pre-match"),  # Solo si es un partido programado ofrece la posibilidad de consultar la previa.
      id_partido=partidos[index].get("id"),  # Id del partido.
      mostrar_historial=True,
      id_partido_football_data=partidos[index].get("id_partido_football_data")  # Id del partido en FootballData.
    )

    await context.bot.edit_message_text(
      chat_id=query.message.chat_id,
      message_id=msg_id,
      text=texto,
      parse_mode="HTML",
      reply_markup=reply_markup
    )
  
  async def maniana(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /maniana.
    """
    estado = "pre-match"
    maniana = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")  # Fecha de mañana.
    partidos = await self._api_service.obtener_partidos_estado_y_fecha(estado, maniana)  # Obtener los partidos.

    if not partidos:
      await update.message.reply_text("❌ No hay partidos para mostrar.")
      return

    # Carga de variables de utilidad:
    scope = "maniana"
    index = 0

    context.user_data["maniana_estado"] = estado
    context.user_data["maniana_partidos"] = partidos
    context.user_data["maniana_index"] = index
    context.user_data["scope_actual"] = scope

    texto = formatear_partido(partidos[index])

    # Construcción del teclado:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=(partidos[index]["estado"] == "pre-match"),  # Solo si es un partido programado ofrece la posibilidad de consultar la previa.
      id_partido=partidos[index].get("id")  # Id del partido a mostrar.
    )

    sent = await update.message.reply_html(texto, reply_markup=reply_markup)
    context.user_data[f"{scope}_message_id"] = sent.message_id
    
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
    await query.answer("⏳ Cargando equipo…")

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
    await query.answer("⏳ Cargando plantel…")

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
    await query.answer("⏳ Cargando entrenador…")
    
    id_equipo = query.data.replace("equipo_entrenador_", "")
    
    try:
      entrenador = await self._api_service.obtener_entrenador(id_equipo)
      mensaje = formatear_entrenador(entrenador)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo entrenador: {e}")
      
  async def equipo_racha_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando racha…")
    
    id_equipo = query.data.replace("equipo_racha_", "")
    
    try:
      racha = await self._api_service.obtener_racha(id_equipo)
      mensaje = formatear_racha(racha, id_equipo)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo racha: {e}")
      
  async def equipo_proximos_partidos_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando próximos partidos…")
    
    id_equipo = query.data.replace("equipo_proximos_partidos_", "")
    
    try:
      proximos_partidos = await self._api_service.obtener_proximos_partidos(id_equipo)
      mensaje = formatear_proximos_partidos(proximos_partidos, id_equipo)
      
      await query.message.reply_html(mensaje)
    except Exception as e:
      await query.message.reply_text(f"❌ Error obteniendo próximos partidos: {e}")
  
  async def jornada(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
      # Si no se pasó un argumento:
      if len(context.args) != 1:
        await update.message.reply_text("❌ Usá: /jornada <número>")
        return

      jornada = int(context.args[0])  # Obtener argumento enviado junto al comando.
      
      # Validar que la jornada esté dentro del dominio:
      if jornada < 1 or jornada > 38:
        await update.message.reply_text("❌ Las jornadas válidas son de la 1 a la 38.")
        return

      # Obtener partidos de la jornada:
      partidos = await self._api_service.obtener_partidos_jornada(jornada)
      if not partidos:
        await update.message.reply_text("❌ No hay partidos para esta jornada.")
        return

      # Carga de variables de utilidad:
      scope = "jornada"
      index = 0

      context.user_data["jornada_partidos"] = partidos
      context.user_data["jornada_index"] = index
      context.user_data["jornada_numero"] = jornada
      context.user_data["scope_actual"] = scope

      texto = formatear_partido(partidos[index])

      # Construcción del teclado:
      reply_markup = teclado_partido(
        scope=scope,  # Para qué comando es el teclado.
        index=index,  # Partido a mostrar.
        total=len(partidos),  # Cantidad de partidos.
        mostrar_previa=(partidos[index]["estado"] == "pre-match"),  # Solo si es un partido programado ofrece la posibilidad de consultar la previa.
        id_partido=partidos[index].get("id"),  # Id del partido.
        mostrar_historial=True,
        id_partido_football_data=partidos[index].get("id_partido_football_data")  # Id del partido en FootballData.
      )

      sent = await update.message.reply_html(texto, reply_markup=reply_markup)
      context.user_data[f"{scope}_message_id"] = sent.message_id

    except Exception as e:
      await update.message.reply_text(f"❌ Error obteniendo la jornada: {e}")

  async def previa_partido_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando previa…")

    # Obtener id del partido:
    _, id = query.data.split("_")
    id_partido = int(id)

    # Obtener previa del partido:
    cache_key = f"previa_{id_partido}"
    previa = context.user_data.get(cache_key)

    # En caso de que no esté en cache, la solicita a la API:
    if not previa:
      previa = await self._api_service.obtener_previa_partido(id_partido)
      context.user_data[cache_key] = previa  # Guarda en cache la previa para reducir solicitudes.

    texto_previa = formatear_previa_partido(previa)
    texto = f"{query.message.text}\n\n{texto_previa}"

    # Carga de variables de utilidad:
    scope = context.user_data["scope_actual"]
    index = context.user_data[f"{scope}_index"]
    partidos = context.user_data[f"{scope}_partidos"]
    
    # Si la solicitud provino de la parte de las jornadas:
    if scope == "jornada":
      # Me interesa saber si ya se solicitó la previa y/o el historial de este partido para habilitar/deshabilitar los botones de consulta:
      jornada = context.user_data["jornada_numero"]
      context.user_data[f"previa_{jornada}_{index}"] = True  # Guardo en el contexto del usuario que ya se solicitó la previa de este partido.
      
      historial_mostrado = context.user_data.get(f"historial_{jornada}_{index}", False)  # Consulto en el contexto del usuario si ya se solicitó el historial de este partido.

    # Construcción del teclado:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=False,  # No se muestra el botón de ver previa ya que se agrega la misma al mensaje del partido.
      id_partido=id_partido,  # Id del partido.
      mostrar_historial=(scope not in ("hoy", "maniana") and not historial_mostrado),  # No se muestra el botón de ver historial ya que se agrega el mismo al mensaje del partido.
      id_partido_football_data=partidos[index].get("id_partido_football_data")  # Id del partido en FootballData.
    )

    await query.message.edit_text(
      texto,
      parse_mode="HTML",
      reply_markup=reply_markup
    )
  
  async def historial_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando historial")

    # Obtener id del partido:
    _, id = query.data.split("_")
    id_partido = int(id)

    # Obtener historial de enfrentamientos:
    cache_key = f"historial_{id_partido}"
    historial = context.user_data.get(cache_key)

    # En caso de que no esté en cache, lo solicita a la API:
    if not historial:
      historial = await self._api_service.obtener_historial_enfrentamientos(id_partido)
      context.user_data[cache_key] = historial  # Guarda en cache el historial para reducir solicitudes.

    texto_historial = formatear_partidos_historial(historial)
    texto = f"{query.message.text}\n\n{texto_historial}"

    # Carga de variables de utilidad:
    scope = context.user_data["scope_actual"]
    index = context.user_data[f"{scope}_index"]
    partidos = context.user_data[f"{scope}_partidos"]
    
    # Si la solicitud provino de la parte de las jornadas:
    if scope == "jornada":
      # Me interesa saber si ya se solicitó la previa y/o el historial de este partido para habilitar/deshabilitar los botones de consulta:
      jornada = context.user_data["jornada_numero"]
      context.user_data[f"historial_{jornada}_{index}"] = True  # Guardo en el contexto del usuario que ya se solicitó el historial de este partido.
      
      previa_mostrada = context.user_data.get(f"previa_{jornada}_{index}", False)  # Consulto en el contexto del usuario si ya se solicitó la previa de este partido.

    # Construcción del teclado:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=(partidos[index]["estado"] == "pre-match" and not previa_mostrada),  # Solo si es un partido programado ofrece la posibilidad de consultar la previa.
      id_partido=partidos[index].get("id"),  # Id del partido.
      mostrar_historial=False,  # No se muestra el botón de ver historial ya que se agrega el mismo al mensaje del partido.
      id_partido_football_data=partidos[index].get("id_partido_football_data")  # Id del partido en FootballData.
    )

    await query.message.edit_text(
      texto,
      parse_mode="HTML",
      reply_markup=reply_markup
    )