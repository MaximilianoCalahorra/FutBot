from datetime import datetime, timedelta
import pycountry
from utils.ligas import LIGAS, DESCRIPCIONES

def datos_liga(id_liga):
  datos_liga = None
  
  for liga in LIGAS.values():
    if liga["football_data"] == id_liga or liga["soccerdata"] == id_liga:
      datos_liga = (liga["nombre"], liga["bandera"], liga["reglas_posiciones"], liga["jornadas"])
      break
  
  return datos_liga

EMOJIS = {
  "champions": "🟦",
  "champions_q": "🔷",
  "europa": "🟧",
  "conference": "🟩",
  "conference_q": "🟢",
  "ascenso": "⬆️",
  "playoff_ascenso": "🔼",
  "repechaje_descenso": "🟨",
  "descenso": "🟥",
  "octavos": "🟦",
  "playoffs": "🔷",
  "no_clasificado": "⬛"
}

def emoji_pos(pos, reglas):
  if not reglas:
    return "    "
  
  for resultado, posiciones in reglas.items():
    if pos in posiciones:
      return EMOJIS.get(resultado, "    ")
  
  return "    "

ORDEN_LEYENDA = [
  "ascenso",
  "playoff_ascenso",
  "champions",
  "champions_q",
  "europa",
  "conference",
  "conference_q",
  "repechaje_descenso",
  "descenso",
  "octavos",
  "playoffs",
  "no_clasificado"
]

def generar_leyenda(reglas_posiciones):
  lineas = []

  for resultado in ORDEN_LEYENDA:
    if resultado in reglas_posiciones:
      emoji = EMOJIS.get(resultado, "")
      texto = DESCRIPCIONES.get(resultado, resultado)
      lineas.append(f"{emoji} {texto}")

  return "\n".join(lineas) + "\n\n"

def formatear_clasificacion_tabla(clasificacion, nombre_liga, bandera, reglas_posiciones):
  texto = f"📊 <b>Tabla de Posiciones – {nombre_liga}</b> {bandera}\n\n"
  
  for equipo in clasificacion:
    pos = equipo["posicion"]
    texto += (
      f"{emoji_pos(pos, reglas_posiciones)} <b>{pos}. {equipo['nombre']}</b>\n"
      f"     ⭐ Pts: {equipo['puntos']}\n"
      f"     🏟️ PJ: {equipo['partidos_jugados']} | G: {equipo['ganados']} E: {equipo['empatados']} P: {equipo['perdidos']}\n"
      f"     ⚽ DG: {equipo['diferencia_gol']} | GF: {equipo['goles_favor']} GC: {equipo['goles_contra']}\n\n"
    )
  
  texto += generar_leyenda(reglas_posiciones)
  
  return texto

from datetime import datetime, timedelta

def convertir_a_zona_horaria_argentina(date_str, time_str=None, postponed=None):
    """
    Convierte fechas en UTC a horario de Argentina (UTC-3).

    Acepta:
    - date_str="26/10/2025", time_str="15:15"
    - date_str="2025-11-09T15:15:00Z", time_str=None

    Devuelve:
    (fecha_arg, hora_arg) → ("dd/mm/YYYY", "HH:MM")
    """

    if time_str:
      # Formato: dd/mm/YYYY + HH:MM
      dt_utc = datetime.strptime(
        f"{date_str} {time_str}",
        "%d/%m/%Y %H:%M"
      )
    else:
      # Formato ISO 8601: 2025-11-09T15:15:00Z
      dt_utc = datetime.strptime(
        date_str,
        "%Y-%m-%dT%H:%M:%SZ"
      )

    # Convertir de UTC a UTC-3
    if postponed == None:
      dt_arg = dt_utc - timedelta(hours=3)
    else:
      dt_arg = dt_utc

    fecha = dt_arg.strftime("%d/%m/%Y")
    hora = dt_arg.strftime("%H:%M")

    return fecha, hora

def formatear_evento(evento, local, visitante):
  if not evento:
    return ""

  tipo = evento["event_type"]
  minuto = evento.get("event_minute", "?")
  jugador = evento.get("player", {}).get("name", "Jugador desconocido")

  equipo = None

  # Solo asignamos equipo si existen:
  if local and visitante:
    if evento.get("team") == "home":
      equipo = local
    elif evento.get("team") == "away":
      equipo = visitante

  # Texto del equipo (si existe):
  texto_equipo = f"({equipo})" if equipo else ""

  match tipo:
    case "goal":
      asistencia = evento.get("assist_player") or {}
      asistidor = asistencia.get("name", "")

      if asistidor:
        texto_asistidor = f"👟 {asistidor}\n"
      else:
        texto_asistidor = ""

      return (
        f"{minuto}' ⚽️ {jugador}\n"
        f"{texto_asistidor}"
        f"{texto_equipo}\n"
      )

    case "penalty_goal":
      return f"{minuto}' ⚽️ (P) {jugador} {texto_equipo}\n"

    case "own_goal":
      return f"{minuto}' ⚽️ (EC) {jugador} {texto_equipo}\n"

    case "yellow_card":
      return f"{minuto}' 🟨 {jugador} {texto_equipo}\n"

    case "red_card":
      return f"{minuto}' 🟥 {jugador} {texto_equipo}\n"

    case "yellow_red_card":
      return f"{minuto}' 🟨 🟥 {jugador} {texto_equipo}\n"

    case "substitution":
      out_p = evento.get("player_out", {}).get("name", "Jugador OUT")
      in_p = evento.get("player_in", {}).get("name", "Jugador IN")

      return (
        f"{minuto}' 🔄 {texto_equipo}\n"
        f"⬆️ {in_p}\n"
        f"⬇️ {out_p}\n"
      )

    case _:
      return f"{minuto}' Evento desconocido: {tipo}\n"

def formatear_eventos(eventos, local, visitante):
  if len(eventos) > 0:
    titulo = "\n📌 Eventos:\n"
    eventos_formateados = "\n".join(formatear_evento(e, local, visitante) for e in eventos)
    return f"{titulo}{eventos_formateados}"
  return "\n"

def formatear_clima(descripcion: str, temp_c: float | None = None) -> str:
  desc = descripcion.lower().strip()

  if any(k in desc for k in ("thunder", "storm", "thundery")):
    texto, emoji = "Tormenta", "⛈️"

  elif any(k in desc for k in ("snow", "sleet", "ice", "freezing")):
    texto, emoji = "Nieve / hielo", "❄️"

  elif any(k in desc for k in ("heavy rain", "torrential", "downpour")):
    texto, emoji = "Lluvia fuerte", "🌧️"

  elif any(k in desc for k in (
    "light rain", "drizzle", "shower", "patchy rain",
    "scattered showers", "intermittent rain"
  )):
    texto, emoji = "Lluvia ligera", "🌦️"

  elif "rain" in desc:
    texto, emoji = "Lluvia", "🌧️"

  elif any(k in desc for k in ("fog", "mist", "haze", "smoke")):
    texto, emoji = "Neblina", "🌫️"

  elif any(k in desc for k in ("overcast", "broken clouds", "mostly cloudy")):
    texto, emoji = "Muy nublado", "☁️"

  elif any(k in desc for k in ("partly cloudy", "few clouds")):
    texto, emoji = "Parcialmente nublado", "🌥️"

  elif "cloud" in desc:
    texto, emoji = "Nublado", "☁️"

  elif any(k in desc for k in ("windy", "breezy", "gusty")):
    texto, emoji = "Ventoso", "💨"

  elif any(k in desc for k in ("sun", "clear", "fair")):
    texto, emoji = "Despejado", "☀️"

  else:
    texto, emoji = "Condiciones variables", "🌡️"

  if temp_c is not None:
    return f"{emoji} {texto} · {round(temp_c)}°C\n"

  return f"{emoji} {texto}\n"

def formatear_expectativa(valor):
  expectativa = "🔥 Expectativa:"
  if valor >= 8.5:
    return f"{expectativa} muy alta\n"
  if valor >= 7:
    return f"{expectativa} alta\n"
  if valor >= 4:
    return f"{expectativa} media\n"
  return f"{expectativa} baja\n"

def formatear_previa_partido(previa):
  partes = []
  
  if previa == None:
    return "ℹ️ La previa del encuentro aún no se encuentra disponible."

  if previa.get("temperatura") and previa.get("descripcion_clima"):
    partes.append(
      formatear_clima(
        previa["descripcion_clima"],
        previa["temperatura"]
      )
    )

  if previa.get("expectativa_partido"):
    partes.append(formatear_expectativa(previa["expectativa_partido"]))

  if previa.get("comentarios"):
    partes.append(f"📝 <b>Previa</b>\n{previa['comentarios']}")

  return "\n".join(partes)

def formatear_informacion_instancia(partido, id_liga):
  instancia = partido.get("instancia", "")
  
  if instancia == "":
    return ""
  
  if id_liga == "CL" and instancia != "liga":
    if instancia == "final":
      texto = "· Final"
    else:
      if partido["jornada"] == 1:
        numero_juego = "(ida)"
      else:
        numero_juego = "(vuelta)"
    
      if instancia == "playoffs":
        texto = "· Playoffs"
      elif instancia == "octavos":
        texto = "· Octavos de final"
      elif instancia == "cuartos":
        texto = "· Cuartos de final"
      else:
        texto = "· Semifinal"
      
      texto += f" {numero_juego} "
  else:
    texto = f"· Jornada {partido['jornada']} "
    
  return texto

def formatear_partido(partido, id_liga=""):
  estado = partido["estado"]
  eventos = partido["eventos"]
  local = partido["local"]
  visitante = partido["visitante"]
  fecha = partido["fecha"]
  hora = partido["hora"]
  
  previa_partido = formatear_previa_partido(partido.get("previa", {}))
  
  # Manejo del caso en que los eventos no se puedan asociar con seguridad a cada equipo:
  local_eventos = None
  visitante_eventos = None
  flag_eventos_sin_equipo = partido.get("flag_eventos_sin_equipo", "NO")
  
  # En caso de que no se encuentre el flag cargado en el partido, sí cargamos el nombre del local o del visitante en cada evento, según corresponda:
  if flag_eventos_sin_equipo == "NO":
    local_eventos = local
    visitante_eventos = visitante
 
  eventos_formateados = formatear_eventos(eventos, local_eventos, visitante_eventos) if eventos else ""
  
  historial = ""
  if partido.get("id_partido_football_data", "") == "":
    historial = f"ℹ️ El historial de enfrentamientos está disponible solo cuando se consulta una jornada específica."

  informacion_instancia = formatear_informacion_instancia(partido, id_liga)

  # Según el estado del partido lo mostramos de diferente manera:
  if estado in ("pre-match", "TIMED", "SCHEDULED"):  # Partido a futuro.
    return (
      f"🕒 {fecha} {hora} {informacion_instancia}\n"
      f"{local} vs {visitante}\n\n"
      f"{historial}\n"
      f"{previa_partido}\n"
    )

  elif estado in ("live", "halftime", "IN_PLAY", "PAUSED"):  # Partido en juego o en el descanso.
    tiempo = f"⏳ En juego - {partido['minutos']}'\n"
    if estado == "halftime":
      tiempo = "⏸️ Descanso\n"
    return (
      f"🕒 {fecha} {hora} {informacion_instancia}\n"
      f"{tiempo}"
      f"{local} {partido['marcador']} {visitante}\n"
      f"{eventos_formateados}\n"
      f"{historial}"
    )
    
  elif estado in ("finished", "FINISHED"):  # Partido finalizado.
    return (
      f"🕒 {fecha} {hora} {informacion_instancia}\n"
      f"🏁 Finalizado\n"
      f"{local} {partido['marcador']} {visitante}\n"
      f"{eventos_formateados}\n"
      f"{historial}"
    )
  
  elif estado in ("postponed", "POSTPONED"):  # Partido pospuesto.
    return (
      f"📅 ➡️ ⚽ Pospuesto {informacion_instancia}\n"
      f"{local} vs {visitante}\n\n"
      f"{historial}"
    )

def formatear_partidos(partidos):
  if not partidos:
    return "❌ No hay partidos programados."

  # Todos los partidos deberían tener misma fecha
  fecha = partidos[0]["fecha"]

  mensaje = f"📅 <b>Partidos del día - {fecha} - La Liga</b>\n\n"

  for p in partidos:
    mensaje += formatear_partido(p)

  return mensaje.strip()

def formatear_goleadores(goleadores, nombre_liga, bandera):
  texto = f"🎯 <b>Goleadores - {nombre_liga}</b> {bandera}\n\n"

  i = 0
  for g in goleadores:
    i += 1
    texto += (
      f"<b>{i}. {g['jugador']}</b>\n"
      f"{g['equipo']}\n"
      f"⚽️ {g['goles']} goles\n\n"
    )

  return texto

def formatear_equipo(equipo):
  texto = (
    f"<b>{equipo['nombre']}</b>\n\n"
    f"🏟️ {equipo['estadio']}\n"
    f"📍 {equipo['direccion']}\n"
    f"📅 Fundación: {equipo['anio_fundacion']}\n"
    f"🌍 Web: {equipo['sitio_web']}\n\n"
    f"👔 Entrenador: {equipo['entrenador']}\n"
    f"👥 Jugadores registrados: {equipo['cantidad_jugadores']}\n\n"
  )
  
  return texto

def formatear_fecha_nacimiento(fecha_iso: str) -> str:
  try:
    return datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
  except Exception:
    return fecha_iso

def formatear_fecha_contrato(fecha_iso: str) -> str:
  try:
    return datetime.strptime(fecha_iso, "%Y-%m").strftime("%m/%Y")
  except Exception:
    return fecha_iso
  
def bandera_pais(nombre_pais: str) -> str:
  try:
    country = pycountry.countries.lookup(nombre_pais)
    return "".join(chr(127397 + ord(c)) for c in country.alpha_2)
  except LookupError:
    return nombre_pais

POSICIONES = {
  # Portería:
  "Goalkeeper": "Arquero",

  # Defensa:
  "Defence": "Defensor",
  "Centre-Back": "Defensor central",
  "Left-Back": "Lateral izquierdo",
  "Right-Back": "Lateral derecho",

  # Mediocampo:
  "Midfield": "Mediocampista",
  "Central Midfield": "Volante central",
  "Defensive Midfield": "Volante defensivo",
  "Attacking Midfield": "Enganche",

  # Delantera:
  "Offence": "Delantero",
  "Centre-Forward": "Delantero centro",
  "Second Striker": "Segundo delantero",
  "Left Wing": "Extremo izquierdo",
  "Right Wing": "Extremo derecho",
  "Left Winger": "Extremo izquierdo",
  "Right Winger": "Extremo derecho",
}

GRUPOS_LABELS = {
  "POR": "🧤 Arqueros",
  "DEF": "🛡️ Defensores",
  "MED": "⚙️ Mediocampistas",
  "DEL": "🎯 Delanteros"
}

ORDEN_GRUPOS = ["POR", "DEF", "MED", "DEL"]

def traducir_posicion(posicion: str) -> str:
  if not posicion:
    return "—"
  return POSICIONES.get(posicion, posicion)

def formatear_jugador(jugador: dict) -> str:
  nombre = jugador["nombre"]
  posicion = traducir_posicion(jugador.get("posicion", ""))
  nacimiento = formatear_fecha_nacimiento(jugador.get("fecha_nacimiento", ""))
  pais = jugador.get("nacionalidad", "")
  bandera = bandera_pais(pais)

  return (
    f"{bandera} <b>{nombre}</b>\n"
    f"👕 {posicion}\n"
    f"🎂 {nacimiento}\n"
  )

def obtener_grupo_posicion(posicion_raw: str) -> str:
  if posicion_raw == "Goalkeeper":
    return "POR"
  if posicion_raw in ["Centre-Back", "Left-Back", "Right-Back", "Defence"]:
    return "DEF"
  if posicion_raw in ["Midfield", "Central Midfield", "Defensive Midfield", "Attacking Midfield"]:
    return "MED"
  return "DEL"

def agrupar_plantel_por_posicion(plantel):
  grupos = {}

  for jugador in plantel:
    clave = obtener_grupo_posicion(jugador.get("posicion", ""))
    grupos.setdefault(clave, []).append(jugador)

  resultado = []
  for clave in ORDEN_GRUPOS:
    if clave in grupos:
      resultado.append((GRUPOS_LABELS[clave], grupos[clave]))

  return resultado

def formatear_grupo_plantel(grupo, jugadores):
  texto = f"<b>{grupo}</b>\n\n"

  for jugador in jugadores:
    texto += formatear_jugador(jugador) + "\n"

  return texto

def formatear_entrenador(entrenador: dict) -> str:
  nombre = entrenador["nombre"]
  nacimiento = formatear_fecha_nacimiento(entrenador.get("fecha_nacimiento", ""))
  pais = entrenador.get("nacionalidad", "")
  bandera = bandera_pais(pais)
  inicio_contrato = formatear_fecha_contrato(entrenador.get("inicio_contrato", "N/A"))
  fin_contrato = formatear_fecha_contrato(entrenador.get("fin_contrato", "N/A"))
  contrato = f"{inicio_contrato} a {fin_contrato}"

  return (
    f"{bandera} <b>{nombre}</b>\n"
    f"🎂 {nacimiento}\n"
    f"📝 Contrato: {contrato}\n"
  )

def obtener_resultado(partido, id_equipo):
  if partido["ganador"] == "DRAW":
    return "➖"

  es_local = partido["local"]["id"] == int(id_equipo)
  gano_local = partido["ganador"] == "HOME_TEAM"
  
  if es_local and gano_local:
    return "✅"
  
  if not es_local and not gano_local:
    return "✅"

  return "❌" 

def formatear_localia(partido, id_equipo):
  localia = "✈️"
  if partido["local"]["id"] == int(id_equipo):
    localia = "🏠"
  return localia

def obtener_instancia(partido):
  return LIGAS["champions_league"]["instancias"][partido["instancia"]]

def formatear_informacion_partido(partido, id_liga):
  if id_liga == "CL":
    texto = f"<b>{partido['fecha']} {partido['hora']}</b> · "
    
    instancia = LIGAS["champions_league"]["instancias"][partido["instancia"]]
    if instancia == "liga":
      texto += f"Jornada {partido['jornada']} "
    else:
      if instancia == "final":
        texto += " Final "
      else:
        if partido["jornada"] == 1:
          numero_juego = "(ida)"
        else:
          numero_juego = "(vuelta)"
      
      if instancia == "playoffs":
        texto += " Playoffs"
      elif instancia == "octavos":
        texto += " Octavos de final"
      elif instancia == "cuartos":
        texto += " Cuartos de final"
      else:
        texto += " Semifinal"
      
      texto += f" {numero_juego} "
  else:
    texto = f"<b>{partido['fecha']} {partido['hora']}</b> · Jornada {partido['jornada']} "
    
  return texto

def formatear_racha(racha, id_equipo, id_liga=""):
  texto = "⚡ <b>Últimos 5 partidos</b>\n\n"

  for partido in racha:
    resultado = obtener_resultado(partido, id_equipo)
    
    localia = formatear_localia(partido, id_equipo)
    
    informacion_partido = formatear_informacion_partido(partido, id_liga)
    
    texto += (
      f"{resultado} {informacion_partido} {localia}\n"
      f"{partido['local']['nombre']} {partido['marcador']} {partido['visitante']['nombre']}\n\n"
    )

  return texto

def formatear_proximos_partidos(partidos, id_equipo, id_liga=""):
  texto = "<b>🗓️ Próximos 5 partidos</b>\n\n"
  
  for partido in partidos:
    localia = formatear_localia(partido, id_equipo)
    
    informacion_partido = formatear_informacion_partido(partido, id_liga)
    
    texto += (
      f"{localia} {informacion_partido}\n"
      f"{partido['local']['nombre']} vs {partido['visitante']['nombre']}\n\n"
    )
  
  return texto

def normalizar_estado_partido(estado, api_origen):
  if api_origen == "soccerdata":
    if estado == "prematch":
      estado = "TIMED"
    elif estado == "live":
      estado = "IN_PLAY"
    elif estado == "finished":
      estado = "FINISHED"
    elif estado == "postponed":
      estado = "POSTPONED"
    elif estado == "halftime":
      estado = "PAUSED"
  elif api_origen == "football_data":
    if estado in ("TIMED", "SCHEDULED"):
        estado = "pre-match"
    elif estado == "IN_PLAY":
      estado = "live"
    elif estado == "FINISHED":
      estado = "finished"
    elif estado == "POSTPONED":
      estado = "postponed"
    elif estado == "PAUSED":
      estado = "halftime"

  return estado

def construir_texto_previa(preview_content: list[dict]) -> str:
  partes = []

  for bloque in preview_content:
    if bloque["name"].startswith("p"):
      partes.append(bloque["content"])

  return "\n\n---\n\n".join(partes)

def formatear_partido_historial(partido):
  local = partido["local"]
  visitante = partido["visitante"]
  fecha = partido["fecha"]
  hora = partido["hora"]
  
  return (
    f"🕒 {fecha} {hora}\n"
    f"🏁 Finalizado\n"
    f"{local} {partido['marcador']} {visitante}\n\n"
  )

def formatear_conteo_resultados_historial(partidos):
  # Nombres de los equipos:
  equipo_1 = partidos[0]["local"]
  equipo_2 = partidos[0]["visitante"]
  
  # Contador de resultados:
  victorias_equipo_1 = 0
  victorias_equipo_2 = 0
  empates = 0
  
  # Contar resultados:
  for p in partidos:
    ganador = p["ganador"]
    if ganador == equipo_1:
      victorias_equipo_1 += 1
    elif ganador == equipo_2:
      victorias_equipo_2 += 1
    else:
      empates += 1
  
  return (
    f"{equipo_1}: {victorias_equipo_1} victoria/s\n"
    f"Empates: {empates}\n"
    f"{equipo_2}: {victorias_equipo_2} victoria/s\n"
  )

def formatear_partidos_historial(partidos):
  if not partidos:
    return "❌ No hay partidos previos entre ambos equipos."

  # Formateo de cada partido:
  mensaje = "📊 <b>Historial</b>\n\n"
  for p in partidos:
    mensaje += formatear_partido_historial(p)
  
  # Formateo del conteo de resultados:
  mensaje += formatear_conteo_resultados_historial(partidos)

  return mensaje.strip()