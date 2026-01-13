import logging
import threading
import os
from bot.futbot import FutBot
from config.config import Config
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurar logging:
logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  level=logging.INFO
)

def start_dummy_server():
  class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
      self.send_response(200)
      self.end_headers()
      self.wfile.write(b"OK")

  port = int(os.environ.get("PORT", 10000))
  logging.info(f"🌐 Dummy HTTP server escuchando en puerto {port}")
  server = HTTPServer(("0.0.0.0", port), Handler)
  server.serve_forever()

# Inicializar e iniciar el bot:
def main():
  """
  Inicializa e inicia FutBot.
  """
  try:
    threading.Thread(target=start_dummy_server, daemon=True).start()
    
    config = Config()
    bot = FutBot(config)
    bot.run()
  except ValueError as e:
    logging.error(f"Error de configuración: {e}")
  except Exception as e:
    logging.exception(f"Error inesperado: {e}")
  
if __name__ == "__main__":
  main()