from telegram import Update
from telegram.ext import ContextTypes
from datetime import date, timedelta
from utils.formatters import formatear_clasificacion_tabla, formatear_partido, formatear_goleadores, formatear_equipo, formatear_entrenador, agrupar_plantel_por_posicion, formatear_grupo_plantel, formatear_racha, formatear_proximos_partidos, formatear_previa_partido, formatear_partidos_historial
from utils.handler_utils import ejecutar_con_manejo
from bot.keyboards import teclado_partido, teclado_partidos_hoy, teclado_equipos, teclado_equipo, teclado_plantel, teclado_menu

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
    
    texto = (
      f"👋 ¡Hola {user.mention_html()}!\n\n"
      "⚽ <b>Bienvenido a FutBot</b>\n"
      "Elegí una opción para comenzar:"
    )
    
    await update.message.reply_html(
      texto,
      reply_markup=teclado_menu()
    )
    
  async def _responder(self, update: Update, context: ContextTypes.DEFAULT_TYPE, texto: str, reply_markup=None, editar=False):
    """
    Responde correctamente tanto a comandos como a callbacks.
    """
    # Caso botón:
    if update.callback_query:
      query = update.callback_query

      if editar:
        await context.bot.edit_message_text(
          chat_id=query.message.chat_id,
          message_id=query.message.message_id,
          text=texto,
          reply_markup=reply_markup,
          parse_mode="HTML"
        )
        return query.message.message_id
      else:
        sent = await query.message.reply_html(
          texto,
          reply_markup=reply_markup
        )
        return sent.message_id

    # Caso comando:
    else:
      sent = await update.message.reply_html(
        texto,
        reply_markup=reply_markup
      )
      return sent.message_id

  async def ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /ayuda o al botón que lo llama.
    """
    texto = (
      "ℹ️ <b>Ayuda — FutBot</b>\n\n"
      "Podés usar los <b>botones</b> para navegar por el bot de forma sencilla 👆\n\n"
      "También podés escribir comandos si lo preferís:\n\n"
      "📊 <b>/tabla</b> — Tabla de posiciones\n"
      "📅 <b>/hoy</b> — Partidos de hoy\n"
      "📅 <b>/maniana</b> — Partidos de mañana\n"
      "🥅 <b>/goleadores</b> — Máximos goleadores\n"
      "🛡️ <b>/equipos</b> — Información de equipos\n"
      "🗓️ <b>/jornada &lt;número&gt;</b> — Partidos de una jornada\n\n"
    )
    
    await self._responder(update, context, texto)
    
  async def menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Redirige el flujo a la funcionalidad que solicitó el usuario mediante el menú.
    """
    query = update.callback_query
    accion = query.data
    
    mensajes = {
      "menu_tabla": "⏳ Cargando tabla de posiciones...",
      "menu_hoy": "⏳ Cargando partidos de hoy...",
      "menu_maniana": "⏳ Cargando partidos de mañana...",
      "menu_goleadores": "⏳ Cargando goleadores...",
      "menu_equipos": "⏳ Cargando equipos...",
      "menu_jornada": "⏳ Cargando jornada...",
      "menu_ayuda": "ℹ️ Mostrando ayuda...",
    }

    await query.answer(
      mensajes.get(accion, "⏳ Cargando.."),
      cache_time=0
    )
    
    if accion == "menu_tabla":
      await self.tabla(update, context)
    
    elif accion == "menu_hoy":
      await self.hoy(update, context)
      
    elif accion == "menu_maniana":
      await self.maniana(update, context)
    
    elif accion == "menu_goleadores":
      await self.goleadores(update, context)
      
    elif accion == "menu_equipos":
      await self.equipos(update, context)
    
    elif accion == "menu_jornada":
      await self.jornada_pedir_callback(update, context)
    
    elif accion == "menu_ayuda":
      await self.ayuda(update, context)
      
  async def hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /hoy o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando partidos de hoy...")
    
    # Armado de la botonera:
    textos = ["🕒 Programados", "⏳ En juego", "🏁 Finalizados", "📅 ➡️ ⚽ Pospuestos"]
    callbacks = ["hoy_partidos_pre-match_0", "hoy_partidos_live_0", "hoy_partidos_finished_0", "hoy_partidos_postponed_0"]
    
    texto = "⚽ Seleccioná un estado de los partidos:"
    teclado = teclado_partidos_hoy(textos, callbacks)
    await self._responder(update, context, texto, teclado)

  async def hoy_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando partidos...")

    _, _, estado, _ = query.data.split("_")  # Obtener estado de los partidos solicitados.

    hoy = date.today().strftime("%d-%m-%Y")  # Fecha de hoy.
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_estado_y_fecha(estado, hoy),
      mensaje_not_found="ℹ️ No hay partidos para mostrar."
    )
    
    if not partidos:
      await query.message.reply_text("ℹ️ No hay partidos para mostrar.")
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
    await query.answer("⏳ Cargando partido...")

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
    Responde al comando /maniana o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando partidos de mañana...")
    
    estado = "pre-match"
    maniana = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")  # Fecha de mañana.
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_estado_y_fecha(estado, maniana),
      mensaje_not_found="ℹ️ No hay partidos para mostrar."
    )
    
    if not partidos:
      await update.message.reply_text("ℹ️ No hay partidos para mostrar.")
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
    
    message_id = await self._responder(
      update,
      context,
      texto,
      reply_markup=reply_markup
    )

    context.user_data[f"{scope}_message_id"] = message_id
    
  async def tabla(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /tabla o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando tabla de posiciones...")
    
    clasificacion = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_clasificacion(),
      mensaje_not_found="ℹ️ No se pudo obtener la tabla de posiciones."
    )
    
    if not clasificacion:
      return
    
    texto = formatear_clasificacion_tabla(clasificacion)
    await self._responder(update, context, texto)
    
  async def goleadores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /goleadores o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando goleadores...")
    
    goleadores = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_goleadores(),
      mensaje_not_found="ℹ️ No se pudo obtener el ranking de goleadores."
    )
    
    if not goleadores:
      return
    
    texto = formatear_goleadores(goleadores)
    await self._responder(update, context, texto)
  
  async def equipos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /equipos o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando equipos...")
    
    # Listado de equipos:
    equipos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_equipos(),
      mensaje_not_found="ℹ️ No se pudo obtener los equipos."
    )
    
    if not equipos:
      return

    texto = "🛡️ Seleccioná un equipo:"
    teclado = teclado_equipos(equipos)
    await self._responder(update, context, texto, teclado)
    
  async def equipo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Botón cliqueado.
    await query.answer("⏳ Cargando equipo...")

    id_equipo = query.data.replace("equipo_seleccionar_", "")  # Obtener id del equipo.

    equipo = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_equipo(id_equipo),  # Obtener equipo por su id.
      mensaje_not_found="ℹ️ No se pudo obtener el equipo."
    )
    
    if not equipo:
      return
    
    mensaje = formatear_equipo(equipo)
    await query.message.reply_html(
      mensaje,
      reply_markup=teclado_equipo(id_equipo)
    )
  
  async def equipo_plantel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando plantel...")

    _, _, id_equipo, index = query.data.split("_")
    index = int(index)

    plantel = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_plantel(id_equipo),
      mensaje_not_found="ℹ️ No se pudo obtener el plantel."
    )
    
    if not plantel:
      return
    
    grupos = agrupar_plantel_por_posicion(plantel)
    
    if index < 0 or index >= len(grupos):
      await query.message.reply_text("ℹ️ No hay más posiciones para mostrar.")
      return

    grupo, jugadores = grupos[index]
    texto = formatear_grupo_plantel(grupo, jugadores)
    
    reply_markup = teclado_plantel(
      index=index,
      total=len(grupos),
      id_equipo=id_equipo
    )

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
    await query.answer("⏳ Cargando entrenador...")
    
    id_equipo = query.data.replace("equipo_entrenador_", "")
    
    entrenador = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_entrenador(id_equipo),
      mensaje_not_found="ℹ️ No se pudo obtener al entrenador."
    )
    
    if not entrenador:
      return
         
    mensaje = formatear_entrenador(entrenador)
    await query.message.reply_html(mensaje)
      
  async def equipo_racha_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando racha...")
    
    id_equipo = query.data.replace("equipo_racha_", "")
    
    racha = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_racha(id_equipo),
      mensaje_not_found="ℹ️ No se pudo obtener la racha."
    )
    
    if not racha:
      return
    
    mensaje = formatear_racha(racha, id_equipo)
    await query.message.reply_html(mensaje)
      
  async def equipo_proximos_partidos_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando próximos partidos...")
    
    id_equipo = query.data.replace("equipo_proximos_partidos_", "")
    
    proximos_partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_proximos_partidos(id_equipo),
      mensaje_not_found="ℹ️ No se pudo obtener los próximos partidos."
    )
    
    if not proximos_partidos:
      return
    
    mensaje = formatear_proximos_partidos(proximos_partidos, id_equipo)
    await query.message.reply_html(mensaje)
  
  async def jornada_pedir_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["esperando_jornada"] = True  # Bandera de que espero que el usuario indique una jornada.

    await query.message.reply_text(
      "📅 Ingresá el número de jornada que querés ver (1–38):"
    )
  
  async def jornada_desde_mensaje(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Este método solo se activa si la bandera de que el usuario va a ingresar una jornada está levantada:
    if not context.user_data.get("esperando_jornada"):
      return

    texto = update.message.text.strip()

    if not texto.isdigit():
      await update.message.reply_text("❌ Ingresá un número válido (1–38).")
      return

    jornada = int(texto)

    if jornada < 1 or jornada > 38:
      await update.message.reply_text("ℹ️ Las jornadas válidas son de la 1 a la 38.")
      return

    # Limpiamos el estado:
    context.user_data.pop("esperando_jornada", None)

    # Reutilizamos la lógica existente:
    await self._mostrar_jornada(update, context, jornada)
  
  async def _mostrar_jornada(self, update, context, jornada: int):
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_jornada(jornada),
      mensaje_not_found="ℹ️ No se pudo obtener los partidos de la jornada."
    )
    
    if not partidos:
      return
    
    scope = "jornada"
    index = 0
    
    context.user_data["jornada_partidos"] = partidos
    context.user_data["jornada_index"] = index
    context.user_data["jornada_numero"] = jornada
    context.user_data["scope_actual"] = scope
    
    texto = formatear_partido(partidos[index])
    
    reply_markup = teclado_partido(
      scope=scope,
      index=index,
      total=len(partidos),
      mostrar_previa=(partidos[index]["estado"] == "pre-match"),
      id_partido=partidos[index].get("id"),
      mostrar_historial=True,
      id_partido_football_data=partidos[index].get("id_partido_football_data")
    )
    
    sent = await self._responder(
      update,
      context,
      texto,
      reply_markup=reply_markup
    )

    context.user_data[f"{scope}_message_id"] = sent
  
  async def jornada(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /jornada <número>
    """    
    if len(context.args) != 1:
      await update.message.reply_text("ℹ️ Usá: /jornada <número>")
      return

    if not context.args[0].isdigit():
      await update.message.reply_text("❌ El número de jornada debe ser válido.")
      return

    jornada = int(context.args[0])

    if jornada < 1 or jornada > 38:
      await update.message.reply_text("ℹ️ Las jornadas válidas son de la 1 a la 38.")
      return
    
    if update.message:
      await update.message.reply_text(f"⏳ Cargando jornada {jornada}...")

    await self._mostrar_jornada(update, context, jornada)

  async def previa_partido_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando previa...")

    # Obtener id del partido:
    _, id = query.data.split("_")
    id_partido = int(id)

    # Obtener previa del partido:
    cache_key = f"previa_{id_partido}"
    previa = context.user_data.get(cache_key)

    # En caso de que no esté en cache, la solicita a la API:
    if not previa:
      previa = await ejecutar_con_manejo(
        update,
        lambda: self._api_service.obtener_previa_partido(id_partido),
        mensaje_not_found="ℹ️ No se pudo obtener la previa del partido."
      )
      context.user_data[cache_key] = previa  # Guarda en cache la previa para reducir solicitudes.

    if not previa:
      return

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
    await query.answer("⏳ Cargando historial...")

    # Obtener id del partido:
    _, id = query.data.split("_")
    id_partido = int(id)

    # Obtener historial de enfrentamientos:
    cache_key = f"historial_{id_partido}"
    historial = context.user_data.get(cache_key)

    # En caso de que no esté en cache, lo solicita a la API:
    if not historial:
      historial = await ejecutar_con_manejo(
        update,
        lambda: self._api_service.obtener_historial_enfrentamientos(id_partido),
        mensaje_not_found="ℹ️ No se pudo obtener el historial."
      )
      context.user_data[cache_key] = historial  # Guarda en cache el historial para reducir solicitudes.

    if not historial:
      return

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