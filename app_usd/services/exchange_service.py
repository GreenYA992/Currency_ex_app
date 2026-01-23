from typing import Type

from django.http import JsonResponse
from django.utils import timezone

from .base import CacheManager, DataBaseManager, RateFetcher
from .currency_fetchers import USDRateFetchers


class ExchangeService:
    """Основной сервис для получения и обработки курсов валют
    каждый экземпляр работает с конкретной валютой
    """

    def __init__(self, currency_fetcher_class: Type[RateFetcher]):
        """
        :param currency_fetcher_class: класс для получения валюты
        """
        if currency_fetcher_class is None:
            raise ValueError("currency_fetcher_class - обязательный параметр")

        # Инициализируем Fetcher
        self.currency_fetcher = currency_fetcher_class()
        self.currency_code = self.currency_fetcher.get_currency_code()

        # Инициализируем менеджер с привязкой к валюте
        self.cache_manager = CacheManager(
            cache_key=f"exchange_last_request_{self.currency_code}", cooldown=10
        )
        self.db_manager = DataBaseManager(currency_code=self.currency_code)

        # Время создания
        self.request_time = timezone.now()

    def _check_request_allowed(self) -> None:
        """
        Проверяем, можно ли выполнить запрос к API
        :return: None
        """
        can_request, message = self.cache_manager.check_make_request()
        if not can_request:
            raise Exception(message)

    def _fetch_exchange_rate(self) -> float:
        """
        Получаем текущий курс от API
        :return: текущий курс валюты
        """
        try:
            return self.currency_fetcher.get_rate()
        except Exception as e:
            print(f"Ошибка при получении курса {self.currency_code}: {e}")
            raise Exception(f"Не удалось получить курс {self.currency_code}: {str(e)}")

    def _save_rate_database(self, rate: float):
        """
        Сохраняем курс в БД
        :param rate: значение курса
        :return: созданный объект ExchangeRate
        """
        try:
            return self.db_manager.save_rate(rate)
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")
            raise Exception(f"Не удалось сохранить в БД: {e}")

    def _update_cache(self) -> None:
        """
        Обновляем кэш времени последнего запроса
        :return: None
        """
        self.cache_manager.update_cache()

    def _get_formatted_history(self, limit: int = 10) -> list:
        """
        Получаем и форматируем историю курсов
        :param limit: количество последних записей
        :return: список отформатированных записей
        """
        try:
            last_rates = self.db_manager.get_last_rates(limit=limit)
            return [rate.to_dict() for rate in last_rates]
        except Exception as e:
            print(f"Ошибка при получении истории: {e}")
            return []

    def _get_fallback_data(self) -> dict:
        """
        Возвращаем данные из БД при ошибке API
        :return: словарь с данными из БД
        """
        try:
            last_rate = self.db_manager.get_last_rate()
            last_rates = self._get_formatted_history()

            return {
                "status": "Ошибка API",
                "message": "Используются данные из БД",
                "currency": self.currency_code,
                "current_rate": float(last_rate.rate) if last_rate else None,
                "last_rates": last_rates,
                "data_source": "database",
                "timestamp": last_rate.timestamp_readable,
            }
        except Exception as e:
            print(f"Ошибка при получении fallback данных: {e}")
            return {
                "status": "error",
                "message": "не удалось получить данные",
                "currency": self.currency_code,
                "current_rate": None,
                "last_rates": [],
                "data_source": None,
                "timestamp": self.request_time.strftime("%d.%m.%Y %H:%M:%S"),
            }

    def execute(self) -> dict:
        """
        Основной метод: получаем курс, сохраняем в БД и получаем результат
        :return: Словарь с результатом
        """
        # Проверяем возможность запроса
        self._check_request_allowed()
        # Получаем курс от API
        current_rate = self._fetch_exchange_rate()
        # Сохраняем в БД
        rate_obj = self._save_rate_database(current_rate)
        # Обновляем кэш
        self._update_cache()
        # Получаем историю
        last_rates = self._get_formatted_history()
        # Формируем ответ
        return {
            # "status": "success", # по желанию
            "currency": self.currency_code,
            "current_rate": current_rate,
            "timestamp": rate_obj.timestamp_readable,
            # "request_id": str(rate_obj.id), # по желанию
            # "data_source": "api", # по желанию
            "last_rates": last_rates,  # список предыдущих запросов
        }

    def get_response(self, request=None) -> JsonResponse:
        """Возвращает JsonResponse с результатом работы сервиса"""
        _request = request
        try:
            result = self.execute()
            return JsonResponse(
                result, json_dumps_params={"indent": 2, "ensure_ascii": False}
            )
        except Exception as e:
            try:
                fallback_data = self._get_fallback_data()
                if fallback_data["current_rate"] is not None:
                    status_code = 200
                else:
                    status_code = 503

                return JsonResponse(
                    fallback_data,
                    json_dumps_params={"indent": 2, "ensure_ascii": False},
                    status=status_code,
                )
            except Exception as fallback_error:
                # если даже fallback не сработал
                return JsonResponse(
                    {
                        "status": "error",
                        "currency": self.currency_code,
                        "message": f"Ошибка: {str(e)}",
                        "fallback_error": str(fallback_error),
                        "current_rate": None,
                        "last_rates": [],
                        "timestamp": self.request_time.strftime("%d.%m.%Y %H:%M:%S"),
                        "data_source": "Error",
                    }
                )


class ExchangeServiceFactory:
    """Фабрика для создания ExchangeService для разных валют"""

    # Регистрируем доступные валюты
    _currency_registry = {
        "USD": USDRateFetchers,
    }

    @classmethod
    def registry_currency(cls, currency_code: str, fetcher_class: Type[RateFetcher]):
        """Регистрируем новую валюту"""
        cls._currency_registry[currency_code.upper()] = fetcher_class

    @classmethod
    def get_supported_currencies(cls) -> list:
        """Возвращаем список доступных валют"""
        return list(cls._currency_registry.keys())

    @classmethod
    def create_service(cls, currency_code: str) -> ExchangeService:
        """
        Создаем сервис для указанной валюты
        :param currency_code: Код валюты (USD)
        :return: ExchangeService для указанной валюты
        """
        currency_code = currency_code.upper()

        if currency_code not in cls._currency_registry:
            supported = ", ".join(cls.get_supported_currencies())
            raise ValueError(
                f"валюта '{currency_code}' не поддерживается. "
                f"Доступные валюты: {supported}"
            )

        fetcher_class = cls._currency_registry[currency_code]
        return ExchangeService(fetcher_class)
