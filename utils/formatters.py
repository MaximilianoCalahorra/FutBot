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