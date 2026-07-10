import aiohttp
from utils.formatters import convertir_a_zona_horaria_argentina, normalizar_estado_partido, construir_texto_previa
from utils.teams import normalizar_equipo, TEAMS
from utils.ligas import LIGAS
from services.http_utils import procesar_respuesta

class ApiService:
  def __init__(self, config, groq_service):
    # API Football Data:
    self._football_data_api_url_base = config.football_data_org_api_base_url
    self._api_key_football_data = config.football_data_org_api_key
    
    # API Soccerdata:
    self._soccerdata_api_url_base = config.soccerdata_api_base_url
    self._api_key_soccerdata = config.soccerdata_api_key
    
    # Groq:
    self._groq_service = groq_service
    
    # Sesión para consultas:
    self._session = aiohttp.ClientSession()
  
  async def obtener_clasificacion(self, id_liga_fd):
    # Endpoint a consultar:
    url = f"{self._football_data_api_url_base}competitions/{id_liga_fd}/standings"

    # Headers:
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)

    # Tabla completa:
    clasificacion_completa = data["standings"][0]["table"]
    
    # Recorrer la tabla y seleccionar campos de interés por equipo:
    clasificacion = []
    for equipo in clasificacion_completa:
      clasificacion.append({
        "posicion": equipo["position"],
        "escudo": equipo["team"]["crest"],
        "nombre": TEAMS[normalizar_equipo(equipo["team"]["name"])]["canonical"],
        "puntos": equipo["points"],
        "partidos_jugados": equipo["playedGames"],
        "goles_favor": equipo["goalsFor"],
        "goles_contra": equipo["goalsAgainst"],
        "diferencia_gol": equipo["goalDifference"],
        "ganados": equipo["won"],
        "empatados": equipo["draw"],
        "perdidos": equipo["lost"]
      })
      
    return clasificacion
  
  async def obtener_partidos_estado_y_fecha(self, estado_partido, fecha, id_liga_sd):
    url = f"{self._soccerdata_api_url_base}matches/?league_id={id_liga_sd}&date={fecha}&auth_token={self._api_key_soccerdata}"
    
    async with self._session.get(url) as response:
      data = await procesar_respuesta(response)
      
    # Obtener la información completa de los partidos:
    stages = data[0].get("stage", []) if data else []

    partidos_completo = []

    if not stages:
      partidos_completo = []

    elif id_liga_sd == "235":
      # En la Ligue 1 a veces los partidos reales están en el segundo stage:
      if len(stages) > 1 and "matches" in stages[1]:
        partidos_completo = stages[1].get("matches", [])
      else:
        partidos_completo = stages[0].get("matches", [])

    else:
      partidos_completo = stages[0].get("matches", [])
    
    partidos = []
    
    for partido in partidos_completo:
      fecha, hora = convertir_a_zona_horaria_argentina(partido["date"], partido["time"])
      
      # Claves de los equipos:
      clave_equipo_local = normalizar_equipo(partido["teams"]["home"]["name"])
      clave_equipo_visitante = normalizar_equipo(partido["teams"]["away"]["name"])
      
      # Solo se consideran partidos None vs None si es de La Liga, sino deben tener los nombres de los equipos:
      if (
        clave_equipo_local is None
        and clave_equipo_visitante is None
        and id_liga_sd != "297"
      ):
        continue
      else:
      
        # Carga de nombres e identificación de partido None vs None si corresponde:
        equipo_local = "None"
        equipo_visitante = "None"
        eventos_sin_equipo = "NO"
        if clave_equipo_local != None and clave_equipo_visitante != None:
          equipo_local = TEAMS[clave_equipo_local]["canonical"]
          equipo_visitante = TEAMS[clave_equipo_visitante]["canonical"]
        else:
          eventos_sin_equipo = "SI"
        
        id_partido = partido["id"]
        estado = partido["status"]
        minutos = partido["minute"]
        marcador_local = partido["goals"]["home_ft_goals"]
        marcador_visitante = partido["goals"]["away_ft_goals"]
        eventos = partido["events"]
        
        if partido["status"] == estado_partido or (estado_partido == "live" and partido["status"] == "halftime"):
          if estado == "pre-match":
            marcador = "vs"
          else:
            marcador = f"{marcador_local} - {marcador_visitante}"
            
          partido_agregar = {
            "id": id_partido,
            "fecha": fecha,
            "hora": hora,
            "estado": estado,
            "minutos": minutos,
            "local": equipo_local,
            "visitante": equipo_visitante,
            "marcador": marcador,
            "eventos": eventos
          }
          
          # Si es un partido None vs None levanto el flag:
          if eventos_sin_equipo == "SI":
            partido_agregar["flag_eventos_sin_equipo"] = "SI"
          
          partidos.append(partido_agregar)
      
    return partidos   
    
  async def obtener_goleadores(self, id_liga_fd):
    url = f"{self._football_data_api_url_base}/competitions/{id_liga_fd}/scorers"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    goleadores_completo = data["scorers"]
    
    goleadores = []
    for registro in goleadores_completo:
      jugador = registro["player"]["name"]
      equipo = TEAMS[normalizar_equipo(registro["team"]["name"])]["canonical"]
      goles = registro["goals"]
      
      goleadores.append({
        "jugador": jugador,
        "equipo": equipo,
        "goles": goles
      })
    
    return goleadores
  
  async def obtener_equipos(self, id_liga_fd):
    """
    Devuelve lista de equipos de La Liga con id y nombre por cada uno de ellos.
    """
    url = f"{self._football_data_api_url_base}/competitions/{id_liga_fd}/teams"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
        
    equipos_completo = data["teams"]
    
    equipos = []
    for equipo in equipos_completo:
      equipos.append({
        "id": equipo["id"],
        "nombre": TEAMS[normalizar_equipo(equipo["name"])]["canonical"]
      })
    
    return equipos
      
  async def obtener_equipo(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    equipo = {
      "nombre": TEAMS[normalizar_equipo(data["name"])]["canonical"],
      "direccion": data["address"],
      "sitio_web": data["website"],
      "anio_fundacion": data["founded"],
      "estadio": data["venue"],
      "entrenador": data["coach"]["name"],
      "cantidad_jugadores": len(data["squad"])
    }
    
    return equipo

  async def obtener_plantel(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    plantel = []
    plantel_completo = data["squad"]
    
    for jugador in plantel_completo:
      jugador = {
        "nombre": jugador["name"],
        "posicion": jugador["position"],
        "fecha_nacimiento": jugador["dateOfBirth"],
        "nacionalidad": jugador["nationality"]
      }
      
      plantel.append(jugador)

    return plantel
  
  async def obtener_entrenador(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    entrenador_completo = data["coach"]
    
    entrenador = {
      "nombre": entrenador_completo["name"],
      "fecha_nacimiento": entrenador_completo["dateOfBirth"],
      "nacionalidad": entrenador_completo["nationality"],
      "inicio_contrato": entrenador_completo['contract']['start'],
      "fin_contrato": entrenador_completo['contract']['until']
    }
    
    return entrenador
  
  async def obtener_racha(self, id_equipo, id_liga_fd):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}/matches"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
        
    todos_partidos = data["matches"]  # Todos los partidos del equipo en la temporada.
    
    partidos_jugados_liga = []
    for partido in todos_partidos:
      estado = partido["status"]
      competencia = partido["competition"]["code"]
      
      # Solo me interesan los partidos de la competición que hayan finalizado:
      if estado == "FINISHED" and competencia == id_liga_fd:
        partidos_jugados_liga.append(partido)

    racha = []
    # De esos partidos de liga finalizados me quedo con los últimos 5:
    for partido in reversed(partidos_jugados_liga[-5:]):
      fecha, hora = convertir_a_zona_horaria_argentina(partido["utcDate"])
      
      # Información de cada partido:
      partido_racha = {
        "fecha": fecha,
        "hora": hora,
        "jornada": partido["matchday"],
        "local": {
          "id": partido["homeTeam"]["id"],
          "nombre": TEAMS[normalizar_equipo(partido["homeTeam"]["name"])]["canonical"]
        },
        "visitante": {
          "id": partido["awayTeam"]["id"],
          "nombre": TEAMS[normalizar_equipo(partido["awayTeam"]["name"])]["canonical"]
        },
        "marcador": self.determinar_marcador_partido(partido, estado),
        "ganador": partido["score"]["winner"],
        "instancia": partido["stage"]
      }
      
      racha.append(partido_racha)
    
    return racha
  
  async def obtener_proximos_partidos(self, id_equipo, id_liga_fd):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}/matches"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    todos_partidos = data["matches"]  # Todos los partidos del equipo en la temporada.
    
    partidos_por_jugar_liga = []
    for partido in todos_partidos:
      estado = partido["status"]
      competencia = partido["competition"]["code"]
      
      # Solo me interesan los partidos de la competición que estén programados a futuro:
      if (estado == "SCHEDULED" or estado == "TIMED") and competencia == id_liga_fd:
        partidos_por_jugar_liga.append(partido)
    
    proximos_partidos = []
    # De esos partidos de liga futuros me quedo con los primeros 5:
    for partido in partidos_por_jugar_liga[:5]:
      fecha, hora = convertir_a_zona_horaria_argentina(partido["utcDate"])
      
      # Información de cada partido:
      partido_por_jugar = {
        "fecha": fecha,
        "hora": hora,
        "jornada": partido["matchday"],
        "local": {
          "id": partido["homeTeam"]["id"],
          "nombre": TEAMS[normalizar_equipo(partido["homeTeam"]["name"])]["canonical"]
        },
        "visitante": {
          "id": partido["awayTeam"]["id"],
          "nombre": TEAMS[normalizar_equipo(partido["awayTeam"]["name"])]["canonical"]
        },
        "instancia": partido["stage"]
      }
      
      proximos_partidos.append(partido_por_jugar)
    
    return proximos_partidos
  
  async def obtener_eventos_partidos_fecha(self, fecha, id_liga_sd):
    # Normalización de la fecha a cómo la espera el endpoint de Soccerdata:
    fecha = fecha.replace("/", "-")
    
    url = f"{self._soccerdata_api_url_base}matches?league_id={id_liga_sd}&date={fecha}&auth_token={self._api_key_soccerdata}"
    
    async with self._session.get(url) as response:
      data = await procesar_respuesta(response)
    
    # Obtener la información completa de los partidos:
    stages = data[0].get("stage", []) if data else []

    partidos_completo = []

    if not stages:
      partidos_completo = []

    elif id_liga_sd == "235":
      # En la Ligue 1 a veces los partidos reales están en el segundo stage:
      if len(stages) > 1 and "matches" in stages[1]:
        partidos_completo = stages[1].get("matches", [])
      else:
        partidos_completo = stages[0].get("matches", [])

    else:
      partidos_completo = stages[0].get("matches", [])
    
    eventos = []
    for partido in partidos_completo:
      clave_equipo_local = normalizar_equipo(partido["teams"]["home"]["name"])
      clave_equipo_visitante = normalizar_equipo(partido["teams"]["away"]["name"])
      
      # Solo traigo eventos que no tengan equipos None, salvo que sea el caso especial de La Liga:
      if (
        clave_equipo_local is None
        and clave_equipo_visitante is None
        and id_liga_sd != "297"
      ):
        continue
      else:
      
        # Selecciono lo que me interesa de cada partido:
        detalle_partido = {
          "id": partido["id"],
          "estado": partido["status"],
          "minutos": partido["minute"],
          "local_key": clave_equipo_local,
          "visitante_key": clave_equipo_visitante,
          "eventos": partido["events"]
        }
        
        eventos.append(detalle_partido)
    
    return eventos
  
  async def obtener_partidos_jornada(self, jornada, id_liga_fd, id_liga_sd):
    url = f"{self._football_data_api_url_base}/competitions/{id_liga_fd}/matches?matchday={jornada}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    partidos_jornada_completo = data["matches"]  # Partidos completos desde la API.
    
    # Normalización de la fecha y la hora de cada encuentro:  
    for partido in partidos_jornada_completo:
      postponed = None
      if partido["status"] == "POSTPONED":
        postponed = "SI"
      partido["fecha"], partido["hora"] = convertir_a_zona_horaria_argentina(partido["utcDate"], postponed=postponed)
    
    # Obtengo valores únicos de las fechas de los partidos para saber de qué día a qué día se juega en la jornada:
    fechas = set(partido["fecha"] for partido in partidos_jornada_completo)
    
    # Obtengo los eventos ocurridos en los partidos por fecha:
    eventos_por_fecha = {}
    for fecha in fechas:
      partidos_con_eventos = await self.obtener_eventos_partidos_fecha(fecha, id_liga_sd)
      eventos_por_fecha[fecha] = partidos_con_eventos  # Los eventos se agrupan por fecha.
    
    partidos_jornada = []
    eventos_huerfanos = None  # La API de Soccerdata suele tener por jornada un partido donde los equipos son None vs None, por lo que tengo que hacer un manejo especial para asociar los eventos a ese partido.
    for partido in partidos_jornada_completo:
      marcador_local = partido["score"]["fullTime"]["home"]
      marcador_visitante = partido["score"]["fullTime"]["away"]
      
      estado = partido["status"]
      if estado == "TIMED" or estado == "SCHEDULED":
        marcador = "vs"
      else:
        marcador = f"{marcador_local} - {marcador_visitante}"
      
      # Conversión del estado en FootballData al de Soccerdata:
      estado = normalizar_estado_partido(estado, "football_data")
      
      # Selecciono los datos que me interesan para cada partido:
      partido_jornada = {
        "id_partido_football_data": partido["id"],
        "fecha": partido["fecha"],
        "hora": partido["hora"],
        "estado": estado,
        "jornada": partido["matchday"],
        # Normalizo el nombre de cada equipo a una clave para poder relacionar ambas APIs con esas claves:
        "local_key": normalizar_equipo(partido["homeTeam"]["name"]),
        "visitante_key": normalizar_equipo(partido["awayTeam"]["name"]),
        "ganador": partido["score"]["winner"],
        "marcador": marcador,
        "eventos": []
      }
      
      # Obtengo el nombre canónico que generé para cada equipo a partir de su clave:
      partido_jornada["local"] = TEAMS[partido_jornada["local_key"]]["canonical"]
      partido_jornada["visitante"] = TEAMS[partido_jornada["visitante_key"]]["canonical"]
      
      # Eventos ocurridos en la fecha del partido:
      eventos_fecha_partido = eventos_por_fecha[partido["fecha"]]
      
      # Recorro esos eventos para encontrar cuál corresponde al partido que estoy iterando:
      for evento_partido in eventos_fecha_partido:
        # El caso de None vs None:
        if evento_partido["local_key"] is None and evento_partido["visitante_key"] is None:
          eventos_huerfanos = evento_partido  # Guardo en una variable auxiliar ese conjunto de eventos.
        
        # El resto de los casos, asocio partidos de FootballData con eventos de Soccerdata si coinciden las claves del equipo local y visitante:
        elif (
          evento_partido["local_key"] == partido_jornada["local_key"]
          and evento_partido["visitante_key"] == partido_jornada["visitante_key"]
        ):
          # Cargo información que me dio Soccerdata sobre los eventos a los partidos que obtuve con FootballData:
          
          partido_jornada["id"] = evento_partido["id"]
          
          partido_jornada["eventos"] = evento_partido["eventos"]
          partido_jornada["minutos"] = evento_partido["minutos"]
          partido_jornada["estado"] = evento_partido["estado"]
          break
      
      partidos_jornada.append(partido_jornada)
    
    # Si hubo algún evento sin asignar a un partido y son de La Liga:
    if eventos_huerfanos and id_liga_sd == "297":
      # Recorro los partidos hasta encontrar el que está sin eventos:
      for partido in partidos_jornada:
        # Si no tiene eventos y no es un partido pospuesto:
        id_partido = partido.get("id", "")
        if id_partido == "":
          # Cargo la información de los eventos en ese partido:
          
          partido["id"] = eventos_huerfanos["id"]
          
          partido["eventos"] = eventos_huerfanos.get("eventos", [])
          partido["minutos"] = eventos_huerfanos.get("minutos")
          partido["estado"] = eventos_huerfanos.get("estado")
          
          # Flag especial para este partido ya que la API de Soccerdata asocia todos los eventos sucedidos al equipo "home", por lo que tengo que manejar este caso especial para que el formateador del partido no muestre a qué equipo pertenece el evento. En el resto de los partidos sí está bien cargado si el evento corresponde a "home" o "away", por lo que sí puedo mencionar con certeza a qué equipo corresponde.
          partido["flag_eventos_sin_equipo"] = "SI"

    return partidos_jornada
  
  async def obtener_previa_partido(self, id_partido):
    url = f"{self._soccerdata_api_url_base}match-preview/?match_id={id_partido}&auth_token={self._api_key_soccerdata}"
    
    async with self._session.get(url) as response:
      data = await procesar_respuesta(response)
    
    if response.status == 400 or response.status == 404 or response.status == 429:
      previa = None
    else:
      comentarios_ingles = construir_texto_previa(data["preview_content"])  # Unión de los comentarios que devuelve la API.
      
      comentarios = self._groq_service.generar_previa(comentarios_ingles)  # Resumen y traducción de los comentarios.
      
      previa = {
        "temperatura": data["match_data"]["weather"]["temp_c"],
        "descripcion_clima": data["match_data"]["weather"]["description"],
        "expectativa_partido": data["match_data"]["excitement_rating"],
        "comentarios": comentarios
      }
    
    return previa
  
  async def obtener_historial_enfrentamientos(self, id_partido, id_liga_fd):
    url = f"{self._football_data_api_url_base}matches/{id_partido}/head2head"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
      
    historial_completo = data["matches"]
    
    # Me interesan solo los partidos de la competencia:
    historial_liga = []
    for partido in historial_completo:
      if partido["competition"]["code"] == id_liga_fd:
        historial_liga.append(partido)
    
    # Me quedo con los últimos partidos que disputaron y extraigo información sobre ellos:
    ultimos_enfrentamientos_liga_completo = historial_liga[:5]
    ultimos_partidos = []
    for enfrentamiento in ultimos_enfrentamientos_liga_completo:
      # Solo me interesan partidos que hayan finalizado:
      if enfrentamiento["status"] == "FINISHED":
        fecha, hora = convertir_a_zona_horaria_argentina(enfrentamiento["utcDate"])

        local = TEAMS[normalizar_equipo(enfrentamiento["homeTeam"]["name"])]["canonical"]
        visitante = TEAMS[normalizar_equipo(enfrentamiento["awayTeam"]["name"])]["canonical"]
        
        ganador_api = enfrentamiento["score"]["winner"]
        if ganador_api == "HOME_TEAM":
          ganador = local
        elif ganador_api == "AWAY_TEAM":
          ganador = visitante
        elif ganador_api == "DRAW":
          ganador = "empate"
        
        # Carga del partido con la información recolectada:
        partido = {
          "fecha": fecha,
          "hora": hora,
          "jornada": enfrentamiento["matchday"],
          "local": local,
          "visitante": visitante,
          "marcador": self.determinar_marcador_partido(partido, "FINISHED"),
          "ganador": ganador
        }
        
        ultimos_partidos.append(partido)
    
    return ultimos_partidos

  async def obtener_partidos_eliminatorias(self, instancia, id_liga_fd):
    url = f"{self._football_data_api_url_base}/competitions/{id_liga_fd}/matches"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await procesar_respuesta(response)
    
    partidos_eliminatorias_completo = data["matches"]  # Partidos completos desde la API.
    
    # Normalización de la fecha y la hora de cada encuentro:  
    for partido in partidos_eliminatorias_completo:
      postponed = None
      if partido["status"] == "POSTPONED":
        postponed = "SI"
      partido["fecha"], partido["hora"] = convertir_a_zona_horaria_argentina(partido["utcDate"], postponed=postponed)
    
    partidos_eliminatoria = []
    for partido in partidos_eliminatorias_completo:
      instancia_partido = LIGAS["champions_league"]["instancias"][partido["stage"]]
      estado = partido["status"]
      
      # Si el partido es de la instancia solicitada y ya están definidos los equipos:
      if instancia_partido == instancia and partido["homeTeam"]["name"] != None and partido["awayTeam"]["name"] != None:
        
        partido_eliminatoria = {
          "id_partido_football_data": partido["id"],
          "fecha": partido["fecha"],
          "hora": partido["hora"],
          "estado": estado,
          "jornada": partido["matchday"],
          "local_key": normalizar_equipo(partido["homeTeam"]["name"]),
          "visitante_key": normalizar_equipo(partido["awayTeam"]["name"]),
          "ganador": partido["score"]["winner"],
          "marcador": self.determinar_marcador_partido(partido, estado),
          "eventos": [],
          "instancia": instancia_partido
        }
        
        # Obtengo el nombre canónico que generé para cada equipo a partir de su clave:
        partido_eliminatoria["local"] = TEAMS[partido_eliminatoria["local_key"]]["canonical"]
        partido_eliminatoria["visitante"] = TEAMS[partido_eliminatoria["visitante_key"]]["canonical"]
      
        partidos_eliminatoria.append(partido_eliminatoria)

    return partidos_eliminatoria
  
  def determinar_marcador_partido(self, partido, estado):
    # Si el partido terminó mediante penales:
    if partido["score"].get("penalties"):
      
      # Diferenciar goles de cada equipo en el partido y en los penales:
      goles_penal_local = partido['score']['penalties']['home']
      goles_penal_visitante = partido['score']['penalties']['away']
      goles_partido_local = partido['score']['fullTime']['home'] - partido['score']['penalties']['home']
      goles_partido_visitante = partido['score']['fullTime']['away'] - partido['score']['penalties']['away']
      
      # Armado del marcador de cada equipo con esa diferenciación visual:
      marcador_local = f"({goles_penal_local}) {goles_partido_local}"
      marcador_visitante = f"{goles_partido_visitante} ({goles_penal_visitante})"
    else:
      marcador_local = partido["score"]["fullTime"]["home"]
      marcador_visitante = partido["score"]["fullTime"]["away"]
    
    # Marcador en texto según el estado del partido:
    if estado == "TIMED":
      marcador = "vs"
    else:
      marcador = f"{marcador_local} - {marcador_visitante}"
    
    return marcador