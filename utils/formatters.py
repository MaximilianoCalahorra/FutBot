from datetime import datetime, timedelta
import pycountry

def emoji_pos(pos):
  if pos <= 4:
      return "🟦"
  if pos == 5:
      return "🟧"
  if pos == 6:
      return "🟩"
  if pos >= 18:
      return "🟥"
  return "    "

def formatear_clasificacion_tabla(clasificacion):
  texto = "📊 <b>Tabla de Posiciones – La Liga</b>\n\n"
  
  for equipo in clasificacion:
    pos = equipo["posicion"]
    texto += (
      f"{emoji_pos(pos)} <b>{pos}. {equipo['nombre']}</b>\n"
      f"     ⭐ Pts: {equipo['puntos']}\n"
      f"     🏟️ PJ: {equipo['partidos_jugados']} | G: {equipo['ganados']} E: {equipo['empatados']} P: {equipo['perdidos']}\n"
      f"     ⚽ DG: {equipo['diferencia_gol']} | GF: {equipo['goles_favor']} GC: {equipo['goles_contra']}\n\n"
    )
  
  texto += (
    f"🟦 Champions League\n"
    f"🟧 Europa League\n"
    f"🟩 Conference League\n"
    f"🟥 Descenso\n\n"
  )
  
  return texto

def convertir_a_zona_horaria_argentina(date_str, time_str):
  """
  Convierte la fecha y hora entregada por la API (en UTC)
  al horario de Argentina (UTC-3).
  Recibe:
    date_str -> "26/10/2025"
    time_str -> "15:15"
  Devuelve:
    (fecha_arg, hora_arg) con formato dd/mm/YYYY y HH:MM
  """

  # La API entrega día/mes/año → hay que parsearlo así:
  dt_utc = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

  # Convertir de UTC a UTC-3:
  dt_arg = dt_utc - timedelta(hours=3)

  # Devolver por separado:
  fecha = dt_arg.strftime("%d/%m/%Y")
  hora = dt_arg.strftime("%H:%M")

  return fecha, hora

def formatear_evento(evento, local, visitante):
  tipo = evento["event_type"]
  minuto = evento.get("event_minute", "?")
  jugador = evento.get("player", {}).get("name", "Jugador desconocido")
  if evento["team"] == "home":
    equipo = local
  else:
    equipo = visitante

  match tipo:
    case "goal":
      asistencia = evento.get("assist_player") or {}
      asistidor = asistencia.get("name", "")

      if asistidor != "":
        texto_asistidor = f"👟 {asistidor}\n"
      else:
        texto_asistidor = asistidor

      return f"{minuto}' ⚽️ {jugador}\n{texto_asistidor}({equipo})\n"

    case "penalty_goal":
      return f"{minuto}' ⚽️ (P) {jugador} ({equipo})\n"
    
    case "own_goal":
      return f"{minuto}' ⚽️ (EC) {jugador} ({equipo})\n"

    case "yellow_card":
      return f"{minuto}' 🟨 {jugador} ({equipo})\n"

    case "red_card":
      return f"{minuto}' 🟥 {jugador} ({equipo})\n"

    case "yellow_red_card":
      return f"{minuto}' 🟨 🟥 {jugador} ({equipo})\n"

    case "substitution":
      out_p = evento.get("player_out", {}).get("name", "Jugador OUT")
      in_p = evento.get("player_in", {}).get("name", "Jugador IN")
      return f"{minuto}' 🔄 ({equipo})\n⬆️ {in_p}\n⬇️ {out_p}\n"

    case _:
      return f"{minuto}' Evento desconocido: {tipo}\n"

def formatear_eventos(eventos, local, visitante):
  return "\n".join(formatear_evento(e, local, visitante) for e in eventos)

def formatear_partido(partido):
  estado = partido["estado"]
  eventos = partido["eventos"]
  local = partido["local"]
  visitante = partido["visitante"]
 
  eventos_formateados = formatear_eventos(eventos, local, visitante) if eventos else ""

  # Según el estado del partido lo mostramos de diferente manera:
  if estado == "pre-match":  # Partido a futuro.
    return (
      f"🕒 {partido['fecha']} {partido['hora']}\n"
      f"{local} vs {visitante}\n\n"
    )

  elif estado == "live":  # Partido en juego.
    return (
      f"⏳ En juego\n"
      f"{local} {partido['marcador']} {visitante}\n"
      f"\n📌 Eventos:\n{eventos_formateados}\n\n"
    )

  elif estado == "finished":  # Partido finalizado.
    return (
      f"🏁 Finalizado\n"
      f"{local} {partido['marcador']} {visitante}\n"
      f"\n📌 Eventos:\n{eventos_formateados}\n\n"
    )

def formatear_partidos(partidos):
  if not partidos:
    return "❌ No hay partidos programados para hoy."

  # Todos los partidos deberían tener misma fecha
  fecha = partidos[0]["fecha"]

  mensaje = f"📅 <b>Partidos del día - {fecha} - La Liga</b>\n\n"

  for p in partidos:
    mensaje += formatear_partido(p)

  return mensaje.strip()

def formatear_goleadores(goleadores):
  texto = "🎯 <b>Goleadores - La Liga</b>\n\n"

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