FROM python:3.7.4-alpine

WORKDIR /app

COPY . ./

CMD [ "python", "server.py" ]