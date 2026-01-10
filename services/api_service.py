import aiohttp
from utils.formatters import convertir_a_zona_horaria_argentina, normalizar_estado_partido, construir_texto_previa
from utils.teams import normalizar_equipo, TEAMS

class ApiService:
  def __init__(self, config, groq_service):
    # API Football Data:
    self._football_data_api_url_base = config.football_data_org_api_base_url
    self._id_liga_football_data = config.id_liga_football_data
    self._api_key_football_data = config.football_data_org_api_key
    
    # API Soccerdata:
    self._soccerdata_api_url_base = config.soccerdata_api_base_url
    self._id_liga_soccerdata = config.id_liga_soccerdata
    self._api_key_soccerdata = config.soccerdata_api_key
    
    # Groq:
    self._groq_service = groq_service
    
    # Sesión para consultas:
    self._session = aiohttp.ClientSession()
  
  async def obtener_clasificacion(self):
    # Endpoint a consultar:
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/standings"

    # Headers:
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }

    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()

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
  
  async def obtener_partidos_estado_y_fecha(self, estado_partido, fecha):
    url = f"{self._soccerdata_api_url_base}matches/?league_id={self._id_liga_soccerdata}&date={fecha}&auth_token={self._api_key_soccerdata}"
    
    async with self._session.get(url) as response:
      data = await response.json()
    
    partidos_completo = data[0]["stage"][0]["matches"] if data[0].get("stage") else []
    partidos = []
    
    for partido in partidos_completo:
      fecha, hora = convertir_a_zona_horaria_argentina(partido["date"], partido["time"])
      
      # Claves de los equipos:
      clave_equipo_local = normalizar_equipo(partido["teams"]["home"]["name"])
      clave_equipo_visitante = normalizar_equipo(partido["teams"]["away"]["name"])
      
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
    
  async def obtener_goleadores(self):
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/scorers"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()
    
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
  
  async def obtener_equipos(self):
    """
    Devuelve lista de equipos de La Liga con id y nombre por cada uno de ellos.
    """
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/teams"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()
        
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
      data = await response.json()
    
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
      data = await response.json()
    
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
      data = await response.json()
    
    entrenador_completo = data["coach"]
    
    entrenador = {
      "nombre": entrenador_completo["name"],
      "fecha_nacimiento": entrenador_completo["dateOfBirth"],
      "nacionalidad": entrenador_completo["nationality"],
      "inicio_contrato": entrenador_completo['contract']['start'],
      "fin_contrato": entrenador_completo['contract']['until']
    }
    
    return entrenador
  
  async def obtener_racha(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}/matches"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()
        
    todos_partidos = data["matches"]  # Todos los partidos del equipo en la temporada.
    
    partidos_jugados_liga = []
    for partido in todos_partidos:
      estado = partido["status"]
      competencia = partido["competition"]["code"]
      
      # Solo me interesan los partidos de liga que hayan finalizado:
      if estado == "FINISHED" and competencia == self._id_liga_football_data:
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
          "nombre": TEAMS[normalizar_equipo(partido["homeTeam"]["name"])]["canonical"],
          "goles": partido["score"]["fullTime"]["home"]
        },
        "visitante": {
          "id": partido["awayTeam"]["id"],
          "nombre": TEAMS[normalizar_equipo(partido["awayTeam"]["name"])]["canonical"],
          "goles": partido["score"]["fullTime"]["away"]
        },
        "ganador": partido["score"]["winner"]
      }
      
      racha.append(partido_racha)
    
    return racha
  
  async def obtener_proximos_partidos(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}/matches"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()
    
    todos_partidos = data["matches"]  # Todos los partidos del equipo en la temporada.
    
    partidos_por_jugar_liga = []
    for partido in todos_partidos:
      estado = partido["status"]
      competencia = partido["competition"]["code"]
      
      # Solo me interesan los partidos de liga que estén programados a futuro:
      if (estado == "SCHEDULED" or estado == "TIMED") and competencia == self._id_liga_football_data:
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
        }
      }
      
      proximos_partidos.append(partido_por_jugar)
    
    return proximos_partidos
  
  async def obtener_eventos_partidos_fecha(self, fecha):
    # Normalización de la fecha a cómo la espera el endpoint de Soccerdata:
    fecha = fecha.replace("/", "-")
    
    url = f"{self._soccerdata_api_url_base}matches?league_id={self._id_liga_soccerdata}&date={fecha}&auth_token={self._api_key_soccerdata}"
    
    async with self._session.get(url) as response:
      data = await response.json()
    
    partidos_completo = data[0]["stage"][0]["matches"] if data[0].get("stage") else []  # Respuesta completa de la API sobre los partidos.
    
    eventos = []
    for partido in partidos_completo:
      # Selecciono lo que me interesa de cada partido:
      detalle_partido = {
        "id": partido["id"],
        "estado": partido["status"],
        "minutos": partido["minute"],
        "local_key": normalizar_equipo(partido["teams"]["home"]["name"]),
        "visitante_key": normalizar_equipo(partido["teams"]["away"]["name"]),
        "eventos": partido["events"]
      }
      
      eventos.append(detalle_partido)
    
    return eventos
  
  async def obtener_partidos_jornada(self, jornada):
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/matches?matchday={jornada}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    async with self._session.get(url, headers=headers) as response:
      data = await response.json()
    
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
      partidos_con_eventos = await self.obtener_eventos_partidos_fecha(fecha)
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

    # Si hubo algún evento sin asignar a un partido:
    if eventos_huerfanos:
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
      data = await response.json()
    
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