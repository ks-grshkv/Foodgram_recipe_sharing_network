FROM python:3.9.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY backend/foodgram/ /app

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]