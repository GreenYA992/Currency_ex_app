from abc import ABC, abstractmethod
from typing import Optional

from django.core.cache import cache
from django.utils import timezone

from app_usd.models import ExchangeRate


class RateFetcher(ABC):
    """Абстрактный класс, для получения курса валют"""

    @abstractmethod
    def get_rate(self) -> float:
        """Возвращает курсы валют"""
        pass

    @abstractmethod
    def get_currency_code(self) -> str:
        """Возвращает код валюты, например (USD)"""
        pass


class CacheManager:
    """Класс для управления кэшем"""

    def __init__(self, cache_key: str, cooldown: int = 10):
        self.cache_key = cache_key
        self.cooldown = cooldown

    def check_make_request(self) -> tuple[bool, str]:
        """Проверяем, таймер запроса"""
        last_request = cache.get(self.cache_key)
        now = timezone.now()

        if last_request and (now - last_request).total_seconds() < self.cooldown:
            time_to_wait = self.cooldown - (now - last_request).total_seconds()
            return False, f"Подождите {int(time_to_wait)} секунд"

        return True, ""

    def update_cache(self):
        """Обновляем время последнего запроса в кэше"""
        cache.set(self.cache_key, timezone.now(), timeout=self.cooldown)


class DataBaseManager:
    """Класс для работы с БД"""

    def __init__(self, currency_code: str):
        """
        :param currency_code: Код валюты с которой работает менеджер
        """
        if not currency_code:
            raise ValueError("Необходимо добавить код валюты")

        self.currency_code = currency_code.upper()

    def save_rate(self, rate: float) -> ExchangeRate:
        """Сохраняем курс валют в БД"""
        return ExchangeRate.objects.create(rate=rate, currency=self.currency_code)

    def get_last_rates(self, limit: int = 10, exclude_latest: bool = False) -> list:
        """Получаем последние 10 запросов, по курсу этой валюты"""
        queryset = ExchangeRate.objects.filter(currency=self.currency_code)
        if exclude_latest:
            # Получаем ID Самой последней записи
            latest = queryset.order_by("-timestamp").first()
            if latest:
                queryset = queryset.exclude(id=latest.id)

        rates = queryset.order_by("-timestamp")[:limit]
        return [rate.to_dict() for rate in rates]

    def get_last_rate(self) -> Optional[ExchangeRate]:
        """Получаем последний сохраненный курс текущий валюты"""
        return ExchangeRate.objects.filter(currency=self.currency_code).latest(
            "timestamp"
        )
