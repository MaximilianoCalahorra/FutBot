from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def teclado_jornada(jornada, index, total, mostrar_previa, id_partido):
  botones = []
  fila = []

  if index > 0:
    fila.append(
      InlineKeyboardButton("⬅️", callback_data=f"jornada_{jornada}_{index - 1}")
    )

  if index < total - 1:
    fila.append(
      InlineKeyboardButton("➡️", callback_data=f"jornada_{jornada}_{index + 1}")
    )

  if fila:
    botones.append(fila)

  if mostrar_previa:
    botones.append([
      InlineKeyboardButton("📝 Ver previa", callback_data=f"previa_partido_{id_partido}")
    ])

  return InlineKeyboardMarkup(botones)