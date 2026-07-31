FROM python:3.10-slim

WORKDIR /app

# Только готовые бинарники, без компиляции
RUN pip install --no-cache-dir --only-binary :all: aiogram==3.10.0 aiohttp==3.9.0 python-dotenv==1.0.0

COPY Botbunkerv3-1.py .

CMD ["python", "Botbunkerv3-1.py"]
