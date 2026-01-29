from typing import Optional

import requests

from app_currency.config import API_SETTINGS, API_URLS, SUPPORTED_CURRENCIES

from .base import RateFetcher


class CBRRateFetcher(RateFetcher):
    """Получаем курс от ЦБ"""

    API_URL = API_URLS["CBR"]
    TIMEOUT = API_SETTINGS["TIMEOUT"]

    def __init__(self, currency_code):
        self.currency = currency_code.upper()

        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Валюта {self.currency} не поддерживается")

    def get_rate(self) -> Optional[float]:
        response = requests.get(self.API_URL, timeout=self.TIMEOUT)
        response.raise_for_status()
        data = response.json()
        rate = data.get("Valute", {}).get(self.currency, {}).get("Value", None)
        return None if rate is None else float(rate)

    def get_currency_code(self) -> str:
        return self.currency
