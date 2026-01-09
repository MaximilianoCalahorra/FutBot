import httpx
from groq import Groq

class GroqService:
  def __init__(self, config):
    # Cliente HTTP para la consulta:
    http_client = httpx.Client(
      timeout=30.0,
      trust_env=False
    )

    # Cliente de la API de Groq:
    self._groq_client = Groq(
      api_key=config.groq_api_key,
      http_client=http_client
    )
    
    # Configuraciones sobre el modelo:
    self._model = "llama-3.3-70b-versatile"
    self._temperature = 0.3
    self._max_tokens = 500
  
  def generar_previa(self, texto_en_ingles):
    try:
      system_prompt = f"""
      Sos un periodista deportivo.

      A partir del texto de previa que se te proporciona en inglés, generá un único párrafo en español que resuma el partido.

      Reglas:
      - Usá solo la información presente en el texto.
      - No inventes datos ni predicciones nuevas.
      - No menciones fechas exactas ni estadísticas muy finas.
      - Extensión aproximada: 70 a 90 palabras.
      - Tono: informativo y natural, apto para un bot de fútbol.
      - No uses emojis.
      - No repitas frases del texto original.
      """
      chat_completion = self._groq_client.chat.completions.create(
        messages = [
          {
            "role": "system",
            "content": system_prompt
          },
          {
            "role": "user",
            "content": texto_en_ingles
          },
        ],
        model = self._model,
        temperature = self._temperature,
        max_tokens = self._max_tokens
      )
    
      return chat_completion.choices[0].message.content.strip()
  
    except Exception as e:
      print(f"No se pudo obtener la respuesta: {str(e)}")
      return None