from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def teclado_partido(scope, index, total, mostrar_previa, id_partido):
  botones = []
  fila = []

  # Si hay partidos antes:
  if index > 0:
    fila.append(
      InlineKeyboardButton("⬅️", callback_data=f"nav_{scope}_{index - 1}")
    )

  # Si hay partidos después:
  if index < total - 1:
    fila.append(
      InlineKeyboardButton("➡️", callback_data=f"nav_{scope}_{index + 1}")
    )

  if fila:
    botones.append(fila)

  # Si el partido tiene su id y hay que mostrar la previa:
  if mostrar_previa and id_partido:
    botones.append([
      InlineKeyboardButton("📝 Ver previa", callback_data=f"previa_{id_partido}")
    ])

  return InlineKeyboardMarkup(botones)