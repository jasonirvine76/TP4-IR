FROM python:3.9-alpine

EXPOSE 8000
WORKDIR /src

RUN apk add --no-cache g++ gcc musl-dev lapack-dev gfortran

RUN apt-get -y install libc-dev
RUN apt-get -y install build-essential
RUN pip install -U pip


COPY requirements.txt /src
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . /src


ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]