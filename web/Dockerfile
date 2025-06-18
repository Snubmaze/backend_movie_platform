FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только зависимости сначала (для оптимизации кэша сборки)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое сервиса в контейнер
COPY . .

# Экспортируем порт, на котором будет работать FastAPI
EXPOSE 8000

# Переменная для более детального логирования Python
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
