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
    self._football_api_key = os.getenv("FOOTBALL_API_KEY")
    
    # Validaciones:
    if not self._telegram_token:
      raise ValueError("No se encontró el token de Telegram. Verificá el archivo .env")

    if not self._football_api_key:
      raise ValueError("No se encontró la API key de Football. Verificá el archivo .env")
    
    # Variables adicionales de configuración:
    self._id_liga = 128  # Liga Profesional Argentina.
    self._temporada = 2025  # Temporada.
    self._football_api_base_url = "https://v3.footbal.api-sports.io/"  # URL base de la API.
  
  # Getters:
  @property
  def telegram_token(self):
    return self._telegram_token
  
  @property
  def football_api_key(self):
    return self._football_api_key
  
  @property
  def id_liga(self):
    return self._id_liga
  
  @property
  def temporada(self):
    return self._temporada
  
  @property
  def football_api_base_url(self):
    return self._football_api_base_url