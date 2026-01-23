from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services.currency_fetchers import USDRateFetchers
from .services.exchange_service import ExchangeServiceFactory

ExchangeServiceFactory.registry_currency("USD", USDRateFetchers)


@require_GET
def get_usd_rate(request):
    """Получаем курс для USD, явно указываем валюту"""
    service = ExchangeServiceFactory.create_service("USD")
    return service.get_response(request)


@require_GET
def get_currency_rate(request, currency_code: str):
    """
    Универсальный способ для всех зарегистрированных валют.
    Пример: /api/currency/USD/
    """

    try:
        service = ExchangeServiceFactory.create_service(currency_code)
        return service.get_response(request)
    except ValueError as e:
        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
                "supported_currencies": ExchangeServiceFactory.get_supported_currencies(),
            },
            status=400,
        )


@require_GET
def get_available_currencies(request):
    """Возвращает список всех доступных валют"""
    return JsonResponse(
        {
            "status": "success",
            "currencies": ExchangeServiceFactory.get_supported_currencies(),
        }
    )
