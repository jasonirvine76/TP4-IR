FROM python:3.9-alpine

EXPOSE 8000
WORKDIR /src


RUN apk add --no-cache --virtual .build-deps g++ gcc libxml2-dev libxslt-dev \
    && apk add libstdc++

RUN pip install numpy scipy gensim

COPY requirements.txt /src
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . /src


ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]