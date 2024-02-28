FROM python:3.12-alpine
WORKDIR /home
COPY source .
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
