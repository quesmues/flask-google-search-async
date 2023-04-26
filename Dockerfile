FROM python:3.10-alpine

WORKDIR /home/flask-api

COPY flask-api .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["hypercorn", "/home/flask-api/app:asgi_app", "--bind", "0.0.0.0:8000"]