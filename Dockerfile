FROM python:3.10-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости с готовыми бинарниками
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Копируем код
COPY Botbunkerv3-1.py .

CMD ["python", "Botbunkerv3-1.py"]
