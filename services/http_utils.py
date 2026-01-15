from services.exceptions import (
  RateLimitError,
  NotFoundError,
  UnauthorizedError,
  ExternalServiceError
)

async def procesar_respuesta(response):
  if response.status == 200:
    return await response.json()

  if response.status == 429:
    retry_after = response.headers.get("Retry-After")
    raise RateLimitError(retry_after)

  if response.status == 401:
    raise UnauthorizedError("Token inválido o expirado")

  if response.status == 400 or response.status == 404:
    raise NotFoundError("Recurso no encontrado")

  raise ExternalServiceError(f"Error externo: {response.status}")
