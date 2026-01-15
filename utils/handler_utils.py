from services.exceptions import (
  RateLimitError,
  NotFoundError,
  ExternalServiceError
)

async def ejecutar_con_manejo(update, accion, *, mensaje_not_found=None):
  try:
    return await accion()

  except RateLimitError:
    await update.effective_message.reply_text(
      "⏳ Se alcanzó el límite de consultas. Probá nuevamente en unos minutos."
    )

  except NotFoundError:
    await update.effective_message.reply_text(
      mensaje_not_found or "❌ No se encontraron datos."
    )

  except ExternalServiceError:
    await update.effective_message.reply_text(
      "⚠️ El servicio está teniendo problemas. Intentá más tarde."
    )

  except Exception:
    await update.effective_message.reply_text(
      "❌ Ocurrió un error inesperado."
    )

  return None