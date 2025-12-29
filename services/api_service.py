import aiohttp
from datetime import datetime
from utils.formatters import convertir_a_zona_horaria_argentina

class ApiService:
  def __init__(self, config):
    # API Football Data:
    self._football_data_api_url_base = config.football_data_org_api_base_url
    self._id_liga_football_data = config.id_liga_football_data
    self._api_key_football_data = config.football_data_org_api_key
    
    # API Soccerdata:
    self._soccerdata_api_url_base = config.soccerdata_api_base_url
    self._id_liga_soccerdata = config.id_liga_soccerdata
    self._api_key_soccerdata = config.soccerdata_api_key
  
  async def obtener_clasificacion(self):
    # Endpoint a consultar:
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/standings"

    # Headers:
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }

    # Consultar:
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        data = await response.json()

    # Tabla completa:
    clasificacion_completa = data["standings"][0]["table"]
    
    # Recorrer la tabla y seleccionar campos de interés por equipo:
    clasificacion = []
    for equipo in clasificacion_completa:
      clasificacion.append({
        "posicion": equipo["position"],
        "escudo": equipo["team"]["crest"],
        "nombre": equipo["team"]["name"],
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
  
  async def obtener_partidos_hoy(self, estado_partido):
    hoy = datetime.today().strftime("%d-%m-%Y")  # Fecha de hoy.
    url = f"https://api.soccerdataapi.com/matches/?league_id={self._id_liga_soccerdata}&date={hoy}&auth_token={self._api_key_soccerdata}"
    
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        data = await response.json()
    
    partidos_completo = data[0]["stage"][0]["matches"] if data[0].get("stage") else []
    partidos = []
    
    for partido in partidos_completo:
      fecha, hora = convertir_a_zona_horaria_argentina(partido["date"], partido["time"])
      equipo_local = partido["teams"]["home"]["name"]
      equipo_visitante = partido["teams"]["away"]["name"]
      estado = partido["status"]
      minutos = partido["minute"]
      marcador_local = partido["goals"]["home_ft_goals"]
      marcador_visitante = partido["goals"]["away_ft_goals"]
      eventos = partido["events"]
      
      if partido["status"] == estado_partido:
        if estado == "pre-match":
          marcador = "vs"
        else:
          marcador = f"{marcador_local} - {marcador_visitante}"
        
        partidos.append({
          "fecha": fecha,
          "hora": hora,
          "estado": estado,
          "minutos": minutos,
          "local": equipo_local,
          "visitante": equipo_visitante,
          "marcador": marcador,
          "eventos": eventos
        })
      
    return partidos
    
  async def obtener_goleadores(self):
    url = f"{self._football_data_api_url_base}/competitions/{self._id_liga_football_data}/scorers"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        data = await response.json()
    
    goleadores_completo = data["scorers"]
    
    goleadores = []
    for registro in goleadores_completo:
      jugador = registro["player"]["name"]
      equipo = registro["team"]["name"]
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
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        data = await response.json()
        
    equipos_completo = data["teams"]
    
    equipos = []
    for equipo in equipos_completo:
      equipos.append({
        "id": equipo["id"],
        "nombre": equipo["name"]
      })
    
    return equipos
      
  async def obtener_equipo(self, id_equipo):
    url = f"{self._football_data_api_url_base}/teams/{id_equipo}"
    
    headers = {
      "X-Auth-Token": self._api_key_football_data,
      "User-Agent": "FutBot/1.0"
    }
    
    # Consultar:
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        data = await response.json()
    
    equipo = {
      "nombre": data["name"],
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
    
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
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
    
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
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
    
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
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
          "nombre": partido["homeTeam"]["name"],
          "goles": partido["score"]["fullTime"]["home"]
        },
        "visitante": {
          "id": partido["awayTeam"]["id"],
          "nombre": partido["awayTeam"]["name"],
          "goles": partido["score"]["fullTime"]["away"]
        },
        "ganador": partido["score"]["winner"]
      }
      
      racha.append(partido_racha)
    
    return racha