from django.http import JsonResponse
from django.views.decorators.http import require_GET

from app_currency.config import SUPPORTED_CURRENCIES

from .services.currency_fetchers import CBRRateFetcher
from .services.exchange_service import ExchangeService


@require_GET
def get_currency_rate(request, currency_code: str):
    """
    Универсальный способ для всех зарегистрированных валют.
    Пример: /get-current-<str:currency_code>/
    или /get-current-usd/
    """
    currency_code = currency_code.upper()
    if currency_code not in SUPPORTED_CURRENCIES:
        return JsonResponse(
            {
                "error": f"Валюта '{currency_code}' не поддерживается",
                "available": SUPPORTED_CURRENCIES,
            },
            status=400,
        )

    fetcher = CBRRateFetcher(currency_code=currency_code)
    service = ExchangeService(fetcher)
    return service.get_response(request)


@require_GET
def get_available_currencies(_request):
    """Возвращает список всех доступных валют"""
    return JsonResponse(
        {"Доступные валюты": SUPPORTED_CURRENCIES},
        json_dumps_params={"ensure_ascii": False},
    )
