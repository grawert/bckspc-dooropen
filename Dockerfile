FROM python:2-alpine

RUN apk add build-base openldap-dev
ADD . /app
RUN pip install -r /app/requirements.txt

CMD ["python", "/app/main.py"]
