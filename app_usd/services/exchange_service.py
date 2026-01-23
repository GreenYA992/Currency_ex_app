from typing import Type

from django.http import JsonResponse
from django.utils import timezone

from .base import CacheManager, DataBaseManager, RateFetcher


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

    def _get_fallback_data(self) -> dict:
        """
        Возвращаем данные из БД при ошибке API
        :return: словарь с данными из БД
        """
        try:
            last_rate = self.db_manager.get_last_rate()
            last_rates = self.db_manager.get_last_rates()

            return {
                "status": "Ошибка API",
                "message": "Используются данные из БД",
                "currency": self.currency_code,
                "current_rate": float(last_rate.rate) if last_rate else None,
                "data_source": "database",
                "timestamp": last_rate.timestamp_readable,
                "last_rates": last_rates,
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
        Делаем запрос.
        Основной метод: получаем курс, сохраняем в БД и получаем результат
        :return: Словарь с результатом
        """
        # Получаем курс от API
        try:
            current_rate = self.currency_fetcher.get_rate()
        except Exception as e:
            print(f"Ошибка при получении курса {self.currency_code}: {e}")
            raise Exception(f"Не удалось получить курс {self.currency_code}: {str(e)}")
        # Сохраняем в БД
        try:
            rate_obj = self.db_manager.save_rate(current_rate)
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")
            raise Exception(f"Не удалось сохранить в БД: {e}")
        # Обновляем кэш
        self.cache_manager.update_cache()
        # Получаем историю
        last_rates = self.db_manager.get_last_rates()
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
        """
        Получаем(выводим) ответ.
        Возвращает JsonResponse с результатом работы сервиса
        :param request: None
        :return: JsonResponse
        """
        _request = request

        # Проверяем кэш
        can_request, message = self.cache_manager.check_make_request()
        if not can_request:
            last_rates = self.db_manager.get_last_rates()
            return JsonResponse(
                {
                    "status": "error",
                    "currency": self.currency_code,
                    "message": str(message),
                    "current_rate": None,
                    "last_rates": last_rates,
                },
                status=429,
                json_dumps_params={"indent": 2, "ensure_ascii": False},
            )

        # Если кэш разрешил, делаем запрос к API
        try:
            result = self.execute()
            return JsonResponse(
                result, json_dumps_params={"indent": 2, "ensure_ascii": False}
            )
        except Exception as e:
            # Ошибка при запросе к API
            try:
                # Пытаемся сделать Fallback
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
                        "timestamp": self.request_time.strftime("%d.%m.%Y %H:%M:%S"),
                        "data_source": "Error",
                        "last_rates": [],
                    },
                    status=429,
                    json_dumps_params={"indent": 2, "ensure_ascii": False},
                )
