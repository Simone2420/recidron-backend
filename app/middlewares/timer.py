import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class TimerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que mide el tiempo de respuesta de cada petición.
    """

    async def dispatch(self, request: Request, call_next):
        # Tiempo inicial
        start_time = time.time()

        # Procesar la petición
        response = await call_next(request)

        # Tiempo final
        process_time = time.time() - start_time

        # Agregar header con el tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)

        # Loggear el tiempo
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )

        return response