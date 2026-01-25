import requests
from typing import Optional
from .base import RateFetcher



class CBRRateFetcher(RateFetcher):
    """Получаем курс от ЦБ"""

    API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    SUPPORTED_CODES = ["USD", "EUR"]

    def __init__(self, currency_code):
        self.currency = currency_code.upper()

        if self.currency not in self.SUPPORTED_CODES:
            raise ValueError(f"Валюта {self.currency} не поддерживается")

    def get_rate(self) -> Optional[float]:
        response = requests.get(self.API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        #if self.currency not in data["Valute"]:
            #raise ValueError(f"Валюта {self.currency} не найдена")

        #return float(data["Valute"][self.currency]["Value"])
        rate = data.get("Valute", {}).get(self.currency, {}).get("Value", None)
        return None if rate is None else float(rate)

    def get_currency_code(self) -> str:
        return self.currency