from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config.config import Config
from bot.command_handler import CommandHandlerBot
from services.api_service import ApiService
from services.groq_service import GroqService
import logging

class FutBot:
  """
  Clase principal del bot que maneja todas las interacciones de Telegram proporcionando información sobre fútbol al usuario.
  """
  
  def __init__(self, config: Config):
    """
    Inicializa el FutBot.
    
    Args:
      config (Config): Objeto de configuración con tokens y parámetros del proyecto.
    """
    # Config:
    self._config = config

    # Telegram:
    self._application = (
      Application.builder()
      .token(config.telegram_token)
      .build()
    )

    # Servicios:
    groq_service = GroqService(config)
    api_service = ApiService(config, groq_service)

    # Handlers:
    self._command_handler = CommandHandlerBot(api_service)
  
  def _register_handlers(self):
    """
    Registra todos los manejadores de comandos.
    """
    self._application.add_handler(CommandHandler("start", self._command_handler.start))
    self._application.add_handler(CommandHandler("ayuda", self._command_handler.ayuda))
    self._application.add_handler(CommandHandler("hoy", self._command_handler.hoy))
    self._application.add_handler(CommandHandler("maniana", self._command_handler.maniana))
    self._application.add_handler(CommandHandler("tabla", self._command_handler.tabla))
    self._application.add_handler(CommandHandler("goleadores", self._command_handler.goleadores))
    self._application.add_handler(CommandHandler("equipos", self._command_handler.equipos))
    self._application.add_handler(CommandHandler("jornada", self._command_handler.jornada))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.equipo_callback, pattern="^equipo_seleccionar_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.equipo_plantel_callback, pattern="^equipo_plantel_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.equipo_entrenador_callback, pattern="^equipo_entrenador_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.equipo_racha_callback, pattern="^equipo_racha_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.equipo_proximos_partidos_callback, pattern="^equipo_proximos_partidos_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.hoy_callback, pattern="^hoy_partidos_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.jornada_callback, pattern="^jornada_"))
    self._application.add_handler(CallbackQueryHandler(self._command_handler.previa_partido_callback, pattern="^previa_partido_"))
  
  def run(self):
    """
    Inicia el bot.
    """
    self._register_handlers()
    logging.info("🤖 FutBot iniciado. Esperando comandos...")
    self._application.run_polling()