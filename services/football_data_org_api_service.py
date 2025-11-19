import aiohttp

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