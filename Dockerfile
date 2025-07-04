FROM python:3.13.5-alpine


COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

WORKDIR /app
COPY ./flaskr/* /app

RUN adduser -u 5678 --disabled-password appuser && chown -R appuser /app
USER appuser

ENTRYPOINT ["python3","-m","flask","--app","api","run","--host=0.0.0.0"]
