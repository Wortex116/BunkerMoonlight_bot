FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Botbunkerv3-1.py .

CMD ["python", "Botbunkerv3-1.py"]
