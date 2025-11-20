FROM python:3.12-slim

# Устанавливаем рабочую папку
WORKDIR /app

# Копируем только зависимости сначала (кеширование)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Открываем порт
EXPOSE 8000

# Команда по умолчанию (переопределяется в docker-compose)
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]