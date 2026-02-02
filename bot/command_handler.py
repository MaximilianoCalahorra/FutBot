from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.formatters import formatear_clasificacion_tabla, formatear_partido, formatear_goleadores, formatear_equipo, formatear_entrenador, agrupar_plantel_por_posicion, formatear_grupo_plantel, formatear_racha, formatear_proximos_partidos, formatear_previa_partido, formatear_partidos_historial, datos_liga
from utils.handler_utils import ejecutar_con_manejo
from bot.keyboards import teclado_partido, teclado_partidos_hoy, teclado_equipos, teclado_equipo, teclado_plantel, teclado_menu_liga, teclado_ligas, teclado_eliminatorias

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
      reply_markup=teclado_ligas("menu_")
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
      "🗓️ <b>/jornada &lt;número&gt;</b> — Partidos de una jornada\n"
      "🗓️ <b>/ligas</b> — Selección de una competición para hacer consultas\n"
      "🗓️ <b>/eliminatorias</b> — Partidos de la Champions League agrupados por instancia\n\n"
    )
    
    await self._responder(update, context, texto)
  
  async def menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando menú de la liga...")
    _, id_liga_football_data, id_liga_soccerdata = query.data.split("_")  # Obtener id de la liga seleccionada en las APIs.
    
    nombre_liga, bandera, reglas_posiciones, jornadas = datos_liga(id_liga_football_data)
    
    context.user_data["liga"] = {
      "fd": id_liga_football_data,
      "sd": id_liga_soccerdata,
      "nombre": nombre_liga,
      "bandera": bandera,
      "reglas_posiciones": reglas_posiciones,
      "jornadas": jornadas
    }
    
    texto = f"¿Qué querés consultar?"
    
    await query.message.reply_html(
      texto,
      reply_markup=teclado_menu_liga(id_liga_football_data)
    )
  
  async def liga_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Redirige el flujo a la funcionalidad que solicitó el usuario mediante el menú.
    """
    query = update.callback_query
    accion = query.data
    
    mensajes = {
      "liga_tabla": "⏳ Cargando tabla de posiciones...",
      "liga_hoy": "⏳ Cargando partidos de hoy...",
      "liga_maniana": "⏳ Cargando partidos de mañana...",
      "liga_ayer": "⏳ Cargando partidos de ayer...",
      "liga_goleadores": "⏳ Cargando goleadores...",
      "liga_equipos": "⏳ Cargando equipos...",
      "liga_jornada": "⏳ Cargando jornada...",
      "liga_ayuda": "ℹ️ Mostrando ayuda...",
      "liga_eliminatorias": "⏳ Cargando eliminatorias..."
    }

    await query.answer(
      mensajes.get(accion, "⏳ Cargando.."),
      cache_time=0
    )
    
    if accion == "liga_tabla":
      await self.tabla(update, context)
    
    elif accion == "liga_hoy":
      await self.hoy(update, context)
      
    elif accion == "liga_maniana":
      await self.maniana(update, context)
      
    elif accion == "liga_ayer":
      await self.ayer(update, context)
    
    elif accion == "liga_goleadores":
      await self.goleadores(update, context)
      
    elif accion == "liga_equipos":
      await self.equipos(update, context)
    
    elif accion == "liga_jornada":
      await self.jornada_pedir_callback(update, context)
    
    elif accion == "liga_ayuda":
      await self.ayuda(update, context)
      
    elif accion == "liga_eliminatorias":
      await self.eliminatorias(update, context)
   
  async def ligas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /ligas.
    """ 
    texto = (
      "⚽ Elegí una de las siguientes ligas:"
    )
    
    await update.message.reply_html(
      texto,
      reply_markup=teclado_ligas("ligas_")
    )
    
  async def ligas_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Liga seleccionada")
    _, id_liga_football_data, id_liga_soccerdata = query.data.split("_")  # Obtener id de la liga seleccionada en las APIs.
    
    nombre_liga, bandera, reglas_posiciones, jornadas = datos_liga(id_liga_football_data)
    
    context.user_data["liga"] = {
      "fd": id_liga_football_data,
      "sd": id_liga_soccerdata,
      "nombre": nombre_liga,
      "bandera": bandera,
      "reglas_posiciones": reglas_posiciones,
      "jornadas": jornadas
    }
    
    texto_base = f"✅ <b>Liga seleccionada:</b> {nombre_liga} {bandera}\n\n"
    
    if "comando_pendiente" in context.user_data:
      comando = context.user_data.pop("comando_pendiente")
      texto = (
        f"{texto_base}"
        f"👉 Ahora podés volver a usar /{comando}\n\n"
        "📌 Cambiar liga → /ligas"
      )
    else:
      texto = (
        f"{texto_base}"
        "A partir de ahora, las consultas se aplicarán a esta competencia.\n\n"
        "📌 Cambiar liga → /ligas"
      )

    await query.message.edit_text(texto, parse_mode="HTML")

  def _liga_seleccionada(self, context: ContextTypes.DEFAULT_TYPE) -> bool:
    return "liga" in context.user_data
  
  async def _pedir_liga(self, update: Update):
    texto = (
      "⚠️ Primero necesitás seleccionar una liga.\n\n"
      "Elegí una a continuación 👇"
    )
    
    await update.message.reply_html(
      texto,
      reply_markup=teclado_ligas("ligas_")
    )
      
  async def hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /hoy o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando partidos de hoy...")
      
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "hoy"
      await self._pedir_liga(update)
      return
    
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
    
    id_liga_sd = context.user_data["liga"]["sd"]

    hoy = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date().strftime("%d-%m-%Y")  # Fecha de hoy.
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_estado_y_fecha(estado, hoy, id_liga_sd),
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
    
    id_liga_fd = context.user_data["liga"]["fd"]

    # Acceder al partido solicitado y formatearlo:
    partido = partidos[index]
    texto = formatear_partido(partido, id_liga_fd)

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
    
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "maniana"
      await self._pedir_liga(update)
      return
    
    id_liga_sd = context.user_data["liga"]["sd"]
    estado = "pre-match"
    maniana = (datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date() + timedelta(days=1)).strftime("%d-%m-%Y")  # Fecha de mañana.
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_estado_y_fecha(estado, maniana, id_liga_sd),
      mensaje_not_found="ℹ️ No hay partidos para mostrar."
    )
    
    if not partidos:
      texto = "ℹ️ No hay partidos para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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
    
  async def ayer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /ayer o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando partidos de ayer...")
    
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "ayer"
      await self._pedir_liga(update)
      return
    
    id_liga_sd = context.user_data["liga"]["sd"]
    estado = "finished"
    ayer = (datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date() - timedelta(days=1)).strftime("%d-%m-%Y")  # Fecha de ayer.
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_estado_y_fecha(estado, ayer, id_liga_sd),
      mensaje_not_found="ℹ️ No hay partidos para mostrar."
    )
    
    if not partidos:
      texto = "ℹ️ No hay partidos para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return

    # Carga de variables de utilidad:
    scope = "ayer"
    index = 0

    context.user_data["ayer_estado"] = estado
    context.user_data["ayer_partidos"] = partidos
    context.user_data["ayer_index"] = index
    context.user_data["scope_actual"] = scope

    texto = formatear_partido(partidos[index])

    # Construcción del teclado:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=False,  # No se muestra la previa porque son partidos finalizados.
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
    
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "tabla"
      await self._pedir_liga(update)
      return
    
    id_liga_fd = context.user_data["liga"]["fd"]
    nombre_liga = context.user_data["liga"]["nombre"]
    bandera = context.user_data["liga"]["bandera"]
    reglas_posiciones = context.user_data["liga"]["reglas_posiciones"]
      
    clasificacion = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_clasificacion(id_liga_fd),
      mensaje_not_found="ℹ️ No se pudo obtener la tabla de posiciones."
    )
    
    if not clasificacion:
      texto = "ℹ️ No hay tabla para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return
    
    texto = formatear_clasificacion_tabla(clasificacion, nombre_liga, bandera, reglas_posiciones)
    await self._responder(update, context, texto)
    
  async def goleadores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /goleadores o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando goleadores...")
      
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "goleadores"
      await self._pedir_liga(update)
      return
    
    id_liga_fd = context.user_data["liga"]["fd"]
    nombre_liga = context.user_data["liga"]["nombre"]
    bandera = context.user_data["liga"]["bandera"]
    
    goleadores = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_goleadores(id_liga_fd),
      mensaje_not_found="ℹ️ No se pudo obtener el ranking de goleadores."
    )
    
    if not goleadores:
      texto = "ℹ️ No hay goleadores para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return
    
    texto = formatear_goleadores(goleadores, nombre_liga, bandera)
    await self._responder(update, context, texto)
  
  async def equipos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /equipos o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando equipos...")
    
    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = "equipos"
      await self._pedir_liga(update)
      return
    
    id_liga_fd = context.user_data["liga"]["fd"]
    
    # Listado de equipos:
    equipos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_equipos(id_liga_fd),
      mensaje_not_found="ℹ️ No se pudo obtener los equipos."
    )
    
    if not equipos:
      texto = "ℹ️ No hay equipos para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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
      texto = "ℹ️ No hay equipo para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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
      texto = "ℹ️ No hay plantel para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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

  async def equipo_entrenador_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando entrenador...")
    
    id_equipo = query.data.replace("equipo_entrenador_", "")
    
    entrenador = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_entrenador(id_equipo),
      mensaje_not_found="ℹ️ No se pudo obtener al entrenador."
    )
    
    if not entrenador:
      texto = "ℹ️ No hay entrenador para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return
         
    mensaje = formatear_entrenador(entrenador)
    await query.message.reply_html(mensaje)
      
  async def equipo_racha_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando racha...")
    
    id_equipo = query.data.replace("equipo_racha_", "")
    
    id_liga_fd = context.user_data["liga"]["fd"]
    
    racha = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_racha(id_equipo, id_liga_fd),
      mensaje_not_found="ℹ️ No se pudo obtener la racha."
    )
    
    if not racha:
      texto = "ℹ️ No hay racha para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return
    
    mensaje = formatear_racha(racha, id_equipo, id_liga_fd)
    await query.message.reply_html(mensaje)
      
  async def equipo_proximos_partidos_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando próximos partidos...")
    
    id_equipo = query.data.replace("equipo_proximos_partidos_", "")
    
    id_liga_fd = context.user_data["liga"]["fd"]
    
    proximos_partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_proximos_partidos(id_equipo, id_liga_fd),
      mensaje_not_found="ℹ️ No se pudo obtener los próximos partidos."
    )
    
    if not proximos_partidos:
      texto = "ℹ️ No hay próximos partidos para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
      return
    
    mensaje = formatear_proximos_partidos(proximos_partidos, id_equipo, id_liga_fd)
    await query.message.reply_html(mensaje)
  
  async def jornada_pedir_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["esperando_jornada"] = True  # Bandera de que espero que el usuario indique una jornada.
    
    jornadas = context.user_data["liga"]["jornadas"]

    await query.message.reply_text(
      f"📅 Ingresá el número de jornada que querés ver (1–{jornadas}):"
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

    jornadas = context.user_data["liga"]["jornadas"]
    if jornada < 1 or jornada > jornadas:
      await update.message.reply_text(f"ℹ️ Las jornadas válidas son de la 1 a la {jornadas}.")
      return

    # Limpiamos el estado:
    context.user_data.pop("esperando_jornada", None)

    # Reutilizamos la lógica existente:
    await self._mostrar_jornada(update, context, jornada)
  
  async def _mostrar_jornada(self, update, context, jornada: int):
    id_liga_fd = context.user_data["liga"]["fd"]
    id_liga_sd = context.user_data["liga"]["sd"]
    
    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_jornada(jornada, id_liga_fd, id_liga_sd),
      mensaje_not_found="ℹ️ No se pudo obtener los partidos de la jornada."
    )
    
    if not partidos:
      texto = "ℹ️ No hay partidos para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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

    if not self._liga_seleccionada(context):
      context.user_data["comando_pendiente"] = f"jornada {jornada}"
      await self._pedir_liga(update)
      return

    jornadas = context.user_data["liga"]["jornadas"]
    if jornada < 1 or jornada > jornadas:
      await update.message.reply_text(f"ℹ️ Las jornadas válidas son de la 1 a la {jornadas}.")
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
      texto = "ℹ️ No hay previa para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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
    
    id_liga_fd = context.user_data["liga"]["fd"]

    # En caso de que no esté en cache, lo solicita a la API:
    if not historial:
      historial = await ejecutar_con_manejo(
        update,
        lambda: self._api_service.obtener_historial_enfrentamientos(id_partido, id_liga_fd),
        mensaje_not_found="ℹ️ No se pudo obtener el historial."
      )
      context.user_data[cache_key] = historial  # Guarda en cache el historial para reducir solicitudes.

    if not historial:
      texto = "ℹ️ No hay historial para mostrar."
      await self._responder(
        update,
        context,
        texto
      )
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
  
  async def eliminatorias(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde al comando /eliminatorias o al botón que lo llama.
    """
    if update.message:
      await update.message.reply_text("⏳ Cargando eliminatorias...")
      
    nombre_liga, bandera, reglas_posiciones, jornadas = datos_liga("CL")
    
    context.user_data["liga"] = {
      "fd": "CL",
      "sd": "",
      "nombre": nombre_liga,
      "bandera": bandera,
      "reglas_posiciones": reglas_posiciones,
      "jornadas": jornadas
    }
    
    # Armado de la botonera:
    texto = (
      f"{bandera} {nombre_liga}\n"
      "⚔️ Seleccioná una instancia:"
    )
    teclado = teclado_eliminatorias()
    await self._responder(update, context, texto, teclado)

  async def eliminatorias_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Cargando partidos de la eliminatoria...")

    _, instancia = query.data.split("_")  # Obtener instancia solicitada de las eliminatorias.
    
    id_liga_fd = context.user_data["liga"]["fd"]

    partidos = await ejecutar_con_manejo(
      update,
      lambda: self._api_service.obtener_partidos_eliminatorias(instancia, id_liga_fd),
      mensaje_not_found="ℹ️ No hay partidos para mostrar."
    )
    
    if not partidos:
      await query.message.reply_text("ℹ️ No hay partidos para mostrar.")
      return

    # Carga de valores útiles:
    scope = "eliminatorias"
    index = 0

    context.user_data["eliminatorias_partidos"] = partidos
    context.user_data["eliminatorias_index"] = index
    context.user_data["scope_actual"] = scope

    texto = formatear_partido(partidos[index], id_liga_fd)
    
    # Construcción del teclado que acompaña a cada partido:
    reply_markup = teclado_partido(
      scope=scope,  # Para qué comando es el teclado.
      index=index,  # Partido a mostrar.
      total=len(partidos),  # Cantidad de partidos.
      mostrar_previa=None, 
      id_partido=None, 
      mostrar_historial=True,
      id_partido_football_data=partidos[index]["id_partido_football_data"]
    )

    sent = await query.message.reply_html(texto, reply_markup=reply_markup)
    context.user_data[f"{scope}_message_id"] = sent.message_id