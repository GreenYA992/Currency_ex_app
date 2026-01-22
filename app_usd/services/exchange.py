import requests
from django.core.cache import cache
from django.utils import timezone

from app_usd.models import ExchangeRate


class ExchangeService:
    CACHE_KEY = "last_exchange_request"
    API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    @classmethod
    def get_usd_rate(cls):
        # Проверяем время последнего запроса
        last_request = cache.get(cls.CACHE_KEY)
        now = timezone.now()

        if last_request and (now - last_request).seconds < 10:
            time_to_wait = 10 - (now - last_request).seconds
            raise Exception(f"Подождите {time_to_wait} секунд, перед следующим запросом")

        # Запрос к API
        response = requests.get(cls.API_URL)
        data = response.json()
        usd_rate = data['Valute']['USD']['Value']

        # Сохраняем в БД и кэш
        ExchangeRate.objects.create(rate=usd_rate)
        cache.set(cls.CACHE_KEY, now, timeout=10)

        return usd_rate