FROM python:3.13.5-alpine

COPY requirements.text .
RUN python3 -m pip install -r requirements.text

WORKDIR /app
COPY ./api/* /app

RUN adduser -u 5678 --disabled-password appuser && chwon -R appuser /app
USER appuser

ENTRYPOINT ["python3","-m","flask","--app","main","run"]
