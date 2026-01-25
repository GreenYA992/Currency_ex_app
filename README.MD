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
cd Curr_exchange_rate 
```
```bash
pip install -r requirements.txt
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

- в currency_fetchers.py, в SUPPORTED_CODES добавляем валюту
- регистрируем его во view.py, в SUPPORTED_CURRENCIES

### Для добавления новой валюты через отдельный Endpoint

- в currency_fetchers.py, в SUPPORTED_CODES добавляем валюту
- регистрируем его во view.py, в SUPPORTED_CURRENCIES
- пишем отдельную view функцию.
- добавляем новый путь в urls

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

# Вопросы по ТЗ 
- Нужно ли включать текущий запрос в эти 10 или только предыдущие?
- Какие данные должны быть в каждой записи истории (курс, время, ID запроса)?
- Нужно ли логировать попытки частых запросов (менее 10 секунд)?
- Планируется ли добавление других валют (EUR, CNY)?
- Нужны ли алерты при недоступности API ЦБ?
- Какую БД использовать (PostgreSQL или SQLite достаточно)?
- Нужно ли 100% покрытие тестами или достаточно критических частей?
- Какие линтеры и форматеры использовать (black, isort, flake8)?

### Первичная оценка 6-7 часов
### Фактическая оценка - 14 часов 