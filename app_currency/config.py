# Поддерживаемые валюты
SUPPORTED_CURRENCIES = ["USD", "EUR"]

# Ссылки на источник данных
API_URLS = {"CBR": "https://www.cbr-xml-daily.ru/daily_json.js"}

# Настройки API
API_SETTINGS = {
    "TIMEOUT": 5,  # Таймаут запроса (сек)
}

# Настройки кэширования
CACHE_SETTINGS = {
    "DEFAULT_COOLDOWN": 10,  # Время между запросами (сек)
    "KEY_PREFIX": "exchange_last_request_",
}

# Настройки базы данных
DB_SETTINGS = {
    "DEFAULT_RATE_LIMIT": 10,  # Количество записей в истории
}

# Настройки ответов
RESPONSE_SETTINGS = {
    "indent": 2,
    "ensure_ascii": False,
}

# Формат времени
TIME_FORMATS = {"DISPLAY": "%d.%m.%Y %H:%M:%S"}
