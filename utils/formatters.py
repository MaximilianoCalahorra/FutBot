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

def convertir_a_zona_horaria_argentina(datetime_str):
  # Convertir del formato ISO con Z al objeto datetime UTC:
  dt_utc = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

  # Convertir a UTC-3 (hora Argentina):
  dt_arg = dt_utc - timedelta(hours=3)

  # Devolver fecha y hora por separado:
  return dt_arg.strftime("%d/%m/%Y"), dt_arg.strftime("%H:%M")

def formatear_partido(partido):
  estado = partido["estado"]

  # Según el estado del partido lo mostramos de diferente manera:
  if estado == "TIMED":  # Partido a futuro.
    fecha_str, hora_str = partido.get("fecha_hora", ("", ""))
    return (
      f"🕒 {fecha_str} {hora_str}\n"
      f"{partido['local']['nombre']} vs {partido['visitante']['nombre']}"
    )

  elif estado in ["IN_PLAY", "PAUSED"]:  # Partido en juego.
    return (
      f"⏳ En juego\n"
      f"{partido['local']['nombre']} {partido['marcador']} {partido['visitante']['nombre']}\n\n"
    )

  elif estado == "FINISHED":  # Partido finalizado.
    return (
      f"🏁 Finalizado\n"
      f"{partido['local']['nombre']} {partido['marcador']} {partido['visitante']['nombre']}\n\n"
    )

def formatear_partidos(partidos):
  if not partidos:
    return "❌ No hay partidos programados para hoy."

  # Todos los partidos deberían tener misma fecha
  fecha, _ = partidos[0].get("fecha_hora", ("Sin fecha", ""))

  mensaje = f"📅 <b>Partidos del día - {fecha}</b>\n\n"

  for p in partidos:
    mensaje += formatear_partido(p)

  return mensaje.strip()