FROM python:3.8-slim

RUN apt-get update && \
    apt-get -y install gcc g++ uwsgi-plugin-python3 && \
    apt-get -y upgrade && \
    pip install --upgrade pip && \
    apt-get autoclean && \
    apt-get autoremove && \
    mkdir /var/run/socket

RUN mkdir /src
COPY requirements.txt /src
ADD mvc /src/mvc
ADD static /src/static
COPY debug.py /src/
COPY logging.conf /src/
COPY uwsgi.ini /src/
COPY app.py /src/

WORKDIR /src

RUN pip install -r requirements.txt

EXPOSE 80
CMD ["uwsgi", "--ini", "uwsgi.ini"]
