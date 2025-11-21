import aiohttp
from datetime import datetime
from utils.formatters import convertir_a_zona_horaria_argentina

class FootballDataOrgApiService:
  def __init__(self, config):
    self._url_base = config.football_data_org_api_base_url
    self._id_liga = config.id_liga
    self._api_key = config.football_data_org_api_key
  
  async def obtener_clasificacion(self):
    # Endpoint a consultar:
    url = f"{self._url_base}/competitions/{self._id_liga}/standings"

    # Headers:
    headers = {
      "X-Auth-Token": self._api_key,
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
  
  async def obtener_partidos_hoy(self):
    url = f"{self._url_base}/competitions/{self._id_liga}/matches"  # Endpoint a consultar.
    hoy = datetime.today().strftime("%Y-%m-%d")  # Fecha de hoy.

    headers = {
      "X-Auth-Token": self._api_key,
      "User-Agent": "FutBot/1.0"
    }

    # Parámetros de la consulta:
    params = {
        "dateFrom": hoy,
        "dateTo": hoy
    }

    # Consultar:
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers, params=params) as response:
        data = await response.json()
            
    partidos_completo = data["matches"]
    
    partidos = []
    for partido in partidos_completo:
      fecha = convertir_a_zona_horaria_argentina(partido["utcDate"])
      estado = partido["status"]
      equipo_local = {
        "escudo": partido["homeTeam"]["crest"],
        "nombre": partido["homeTeam"]["name"],
        "sigla_oficial": partido["homeTeam"]["tla"]
      }
      equipo_visitante = {
        "escudo": partido["awayTeam"]["crest"],
        "nombre": partido["awayTeam"]["name"],
        "sigla_oficial": partido["awayTeam"]["tla"]
      }

      goles_local = partido["score"]["fullTime"]["home"] or 0
      goles_visitante = partido["score"]["fullTime"]["away"] or 0

      # Si no hay score todavía:
      if goles_local is None or goles_visitante is None:
          marcador = "vs"
      else:
          marcador = f"{goles_local} - {goles_visitante}"
      
      partidos.append({
          "fecha_hora": fecha,
          "estado": estado,
          "local": equipo_local,
          "visitante": equipo_visitante,
          "marcador": marcador
      })

    return partidos