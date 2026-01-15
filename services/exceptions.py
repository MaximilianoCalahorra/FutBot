class ApiError(Exception):
  pass

class RateLimitError(ApiError):
  def __init__(self, retry_after=None):
    self.retry_after = retry_after
    super().__init__("Límite de consultas alcanzado")

class NotFoundError(ApiError):
  pass

class UnauthorizedError(ApiError):
  pass

class ExternalServiceError(ApiError):
  pass
