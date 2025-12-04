import os
from dotenv import load_dotenv

class Config:
  """
  Clase encargada de generar y exponer la configuración del proyecto.
  """
  def __init__(self):
    # Cargar las variables de entorno desde el archivo .env:
    load_dotenv()
    
    # Variables de entorno principales:
    self._telegram_token = os.getenv("TELEGRAM_TOKEN")
    self._football_data_org_api_key = os.getenv("FOOTBALL_DATA_ORG_API_KEY")
    self._soccerdata_api_key = os.getenv("SOCCERDATA_API_KEY")
    
    # Validaciones:
    if not self._telegram_token:
      raise ValueError("No se encontró el token de Telegram. Verificá el archivo .env")

    if not self._football_data_org_api_key:
      raise ValueError("No se encontró la API key de Football Data. Verificá el archivo .env")
    
    if not self._soccerdata_api_key:
      raise ValueError("No se encontró la API key de Soccerdata. Verificá el archivo .env")
    
    # Variables adicionales de configuración:
    self._id_liga_football_data = "PD"  # La Liga.
    self._id_liga_soccerdata = 297  # La Liga.
    self._football_data_org_api_base_url = "https://api.football-data.org/v4/"
    self._soccerdata_api_base_url = "https://api.soccerdataapi.com/"
  
  # Getters:
  @property
  def telegram_token(self):
    return self._telegram_token
  
  @property
  def football_data_org_api_key(self):
    return self._football_data_org_api_key
  
  @property
  def id_liga_football_data(self):
    return self._id_liga_football_data
  
  @property
  def football_data_org_api_base_url(self):
    return self._football_data_org_api_base_url
  
  @property
  def soccerdata_api_key(self):
    return self._soccerdata_api_key
  
  @property
  def id_liga_soccerdata(self):
    return self._id_liga_soccerdata
  
  @property
  def soccerdata_api_base_url(self):
    return self._soccerdata_api_base_url