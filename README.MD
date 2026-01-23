# Currency Exchange Rate API

#### Django REST API для получения актуальных курсов валют от ЦБ РФ

## Возможности
- Получение текущего курса USD. Переход по ссылке http://127.0.0.1:8000/get-current-usd/ (как в ТЗ) или через динамическую ссылку http://127.0.0.1:8000/currency/usd/
- История последних 10 запросов, в каждой валюте.
- Автоматическое кэширование, защита от частых запросов
- Fallback на данные из БД, при недоступности API ЦБ
- Легкое добавление новых валют

## Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/GreenYA992/Curr_exchange_rate
```
### 2. Создание виртуального окружения 
```bash
python -m venv venv
```
- Активация на Windows
```bash
venv\Scripts\activate
```
- Активация на Linux/Mac
```bash
source venv/bin/activate
```
### 3. Установка зависимостей 
```bash
pip install requirements.txt
```
### 4. Настройка БД
```bash
python manage.py migrate
```
### 5. Запуск сервера
```bash
python manage.py runserver
```
- Сервер будет доступен по адресу http://127.0.0.1:8000

## API Endpoints

### Получить курс USD (как в ТЗ)
```text
/get-current-usd/
```
### Динамический Endpoint (удобнее и универсальнее)

- вместо /usd/ может быть другая валюта, пока добавил только /eur/
```text
/currency/usd/
```

### Для добавления новой валюты (Динамический Endpoint)

- создаем новый класс в currency_fetchers
- регистрируем его во view, в CURRENCY_MAPPING

### Для добавления новой валюты через отдельный Endpoint

- создаем новый класс в currency_fetchers
- регистрируем его во view, в CURRENCY_MAPPING
- пишем новый Endpoint для него 

## Curl
- Курс USD
```bash
curl http://127.0.0.1:8000/get-current-usd/
```
- Курс USD
```bash
curl http://127.0.0.1:8000/currency/usd/
```
- Курс EUR
```bash
curl http://127.0.0.1:8000/currency/eur/
```
- Список доступных валют
```bash
curl http://127.0.0.1:8000/currencies
```