from .base import RateFetcher
import requests

class USDRateFetchers(RateFetcher):
    """Получаем курс USD от ЦБ"""

    API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    def get_rate(self) -> float:
        response = requests.get(self.API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data['Valute']['USD']['Value'])

    def get_currency_code(self) -> str:
        return "USD"