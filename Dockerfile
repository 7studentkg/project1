FROM python:3.8


WORKDIR /usr/src/app

COPY requirements.txt ./

COPY . .

RUN apt-get update

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt && python manage.py collectstatic --noinput
