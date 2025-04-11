FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install flask flask-cors firebase-admin

CMD ["python", "Handleliste-Backend.py"]
