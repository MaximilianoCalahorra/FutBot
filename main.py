import logging
from bot.futbot import FutBot
from config.config import Config

# Configurar logging:
logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  level=logging.INFO
)

# Inicializar e iniciar el bot:
def main():
  """
  Inicializa e inicia FutBot.
  """
  try:
    config = Config()
    bot = FutBot(config)
    bot.run()
  except ValueError as e:
    logging.error(f"Error de configuración: {e}")
  except Exception as e:
    logging.exception(f"Error inesperado: {e}")
  
if __name__ == "__main__":
  main()