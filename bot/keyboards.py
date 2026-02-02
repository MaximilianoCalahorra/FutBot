from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.ligas import LIGAS

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

def teclado_ligas(callback):
  pl = LIGAS["premier_league"]
  ll = LIGAS["la_liga"]
  ch = LIGAS["championship"]
  bu = LIGAS["bundesliga"]
  sa = LIGAS["serie_a"]
  l1 = LIGAS["ligue_1"]
  er = LIGAS["eredivisie"]
  prl = LIGAS["primeira_liga"]
  cl = LIGAS["champions_league"]
  
  return InlineKeyboardMarkup([
    [
      InlineKeyboardButton(f"{pl['bandera']} {pl['nombre']}", callback_data=f"{callback}{pl['football_data']}_{pl['soccerdata']}"),
      InlineKeyboardButton(f"{ch['bandera']} {ch['nombre']}", callback_data=f"{callback}{ch['football_data']}_{ch['soccerdata']}")
    ],
    [
      InlineKeyboardButton(f"{ll['bandera']} {ll['nombre']}", callback_data=f"{callback}{ll['football_data']}_{ll['soccerdata']}"),
      InlineKeyboardButton(f"{bu['bandera']} {bu['nombre']}", callback_data=f"{callback}{bu['football_data']}_{bu['soccerdata']}")
    ],
    [
      InlineKeyboardButton(f"{sa['bandera']} {sa['nombre']}", callback_data=f"{callback}{sa['football_data']}_{sa['soccerdata']}"),
      InlineKeyboardButton(f"{l1['bandera']} {l1['nombre']}", callback_data=f"{callback}{l1['football_data']}_{l1['soccerdata']}")
    ],
    [
      InlineKeyboardButton(f"{prl['bandera']} {prl['nombre']}", callback_data=f"{callback}{prl['football_data']}_{prl['soccerdata']}"),
      InlineKeyboardButton(f"{er['bandera']} {er['nombre']}", callback_data=f"{callback}{er['football_data']}_{er['soccerdata']}")
    ],
    [
      InlineKeyboardButton(f"{cl['bandera']} {cl['nombre']}", callback_data=f"{callback}{cl['football_data']}_{cl['soccerdata']}")
    ]
  ])
  
def teclado_menu_liga(id_liga):
  filas = [
    [
      InlineKeyboardButton("📊 Tabla", callback_data="liga_tabla"),
      InlineKeyboardButton("🥅 Goleadores", callback_data="liga_goleadores")
    ],
    [
      InlineKeyboardButton("📅 Hoy", callback_data="liga_hoy"),
      InlineKeyboardButton("📅 Mañana", callback_data="liga_maniana")
    ],
    [
      InlineKeyboardButton("📅 Ayer", callback_data="liga_ayer"),
      InlineKeyboardButton("🗓️ Jornada", callback_data="liga_jornada")
    ]
  ]

  if id_liga == "CL":
    filas.extend([
      [
        InlineKeyboardButton("⚔️ Eliminatorias", callback_data="liga_eliminatorias"),
        InlineKeyboardButton("🛡️ Equipos", callback_data="liga_equipos")
      ],
      [
        InlineKeyboardButton("ℹ️ Ayuda", callback_data="liga_ayuda")
      ]
    ])
  else:
    filas.append([
      InlineKeyboardButton("🛡️ Equipos", callback_data="liga_equipos"),
      InlineKeyboardButton("ℹ️ Ayuda", callback_data="liga_ayuda")
    ])

  return InlineKeyboardMarkup(filas)

def teclado_eliminatorias():
  return InlineKeyboardMarkup([
    [
      InlineKeyboardButton("🔷 Playoffs", callback_data="eliminatorias_playoffs"),
      InlineKeyboardButton("⚔️ Octavos", callback_data="eliminatorias_octavos")
    ],
    [
      InlineKeyboardButton("🎯 Cuartos", callback_data="eliminatorias_cuartos"),
      InlineKeyboardButton("🔥 Semis", callback_data="eliminatorias_semis")
    ],
    [
      InlineKeyboardButton("🏆 Final", callback_data="eliminatorias_final")
    ]
  ])