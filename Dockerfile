FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]