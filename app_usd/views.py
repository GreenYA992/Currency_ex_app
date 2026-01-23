from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services.currency_fetchers import EURRateFetchers, USDRateFetchers
from .services.exchange_service import ExchangeService

CURRENCY_MAPPING = {
    "USD": USDRateFetchers,
    "EUR": EURRateFetchers,
}


@require_GET
def get_usd_rate(request):
    """Получаем курс для USD, явно указываем валюту"""
    service = ExchangeService(USDRateFetchers)
    return service.get_response(request)


@require_GET
def get_currency_rate(request, currency_code: str):
    """
    Универсальный способ для всех зарегистрированных валют.
    Пример: /currency/USD/
    """
    currency_code = currency_code.upper()
    if currency_code not in CURRENCY_MAPPING:
        return JsonResponse(
            {
                "error": f"Валюта '{currency_code}' не поддерживается",
                "available": list(CURRENCY_MAPPING.keys()),
            },
            status=400,
        )
    fetcher_class = CURRENCY_MAPPING[currency_code]
    service = ExchangeService(fetcher_class)
    return service.get_response(request)


@require_GET
def get_available_currencies(request):
    """Возвращает список всех доступных валют"""
    _request = request
    return JsonResponse(
        {"Доступные валюты": list(CURRENCY_MAPPING.keys())},
        json_dumps_params={"ensure_ascii": False},
    )
