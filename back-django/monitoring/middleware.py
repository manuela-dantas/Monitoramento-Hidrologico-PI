import logging

from .utils import error_response

logger = logging.getLogger(__name__)


class JsonErrorMiddleware:
    """Transforma exceções não tratadas em JSON 500, sem stack trace."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception('Erro inesperado em %s', request.path)
        return error_response(500, 'internal_error', 'Não foi possível carregar os dados.')