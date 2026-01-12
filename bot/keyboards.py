from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def teclado_partido(scope, index, total, mostrar_previa, id_partido, mostrar_historial=False, id_partido_football_data=None):
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
  
  # Si el partido tiene su id y hay que mostrar el historial:
  if mostrar_historial and id_partido_football_data:
    botones.append([
      InlineKeyboardButton("📊 Ver historial", callback_data=f"historial_{id_partido_football_data}")
    ])

  return InlineKeyboardMarkup(botones)

def teclado_partidos_hoy(textos, callbacks):
  botonera = []
  for i in range(len(textos)):
    botonera.append([
      InlineKeyboardButton(
        text=textos[i],
        callback_data=callbacks[i]
      )
    ])
  
  return InlineKeyboardMarkup(botonera)

def teclado_equipos(equipos):
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
  
  return InlineKeyboardMarkup(botonera)

def teclado_equipo(id_equipo):
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
  
  return InlineKeyboardMarkup(botonera)

def teclado_plantel(index, total, id_equipo):
  botonera = []
  
  if index > 0:
    botonera.append(
      InlineKeyboardButton("⬅️", callback_data=f"equipo_plantel_{id_equipo}_{index - 1}")
    )
  
  if index < total - 1:
    botonera.append(
      InlineKeyboardButton("➡️", callback_data=f"equipo_plantel_{id_equipo}_{index + 1}")
    )
  
  return InlineKeyboardMarkup([botonera])