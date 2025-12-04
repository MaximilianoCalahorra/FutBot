from datetime import datetime, timedelta

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

# def convertir_a_zona_horaria_argentina(datetime_str):
#   # Convertir del formato ISO con Z al objeto datetime UTC:
#   dt_utc = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

#   # Convertir a UTC-3 (hora Argentina):
#   dt_arg = dt_utc - timedelta(hours=3)

#   # Devolver fecha y hora por separado:
#   return dt_arg.strftime("%d/%m/%Y"), dt_arg.strftime("%H:%M")

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

# def formatear_partido(partido):
#   estado = partido["estado"]

#   # Según el estado del partido lo mostramos de diferente manera:
#   if estado == "TIMED":  # Partido a futuro.
#     fecha_str, hora_str = partido.get("fecha_hora", ("", ""))
#     return (
#       f"🕒 {fecha_str} {hora_str}\n"
#       f"{partido['local']['nombre']} vs {partido['visitante']['nombre']}"
#     )

#   elif estado in ["IN_PLAY", "PAUSED"]:  # Partido en juego.
#     return (
#       f"⏳ En juego\n"
#       f"{partido['local']['nombre']} {partido['marcador']} {partido['visitante']['nombre']}\n\n"
#     )

#   elif estado == "FINISHED":  # Partido finalizado.
#     return (
#       f"🏁 Finalizado\n"
#       f"{partido['local']['nombre']} {partido['marcador']} {partido['visitante']['nombre']}\n\n"
#     )

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