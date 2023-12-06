FROM python:3.10-slim

EXPOSE 8000
WORKDIR /src

RUN apt-get update && apt-get install -y gcc

COPY requirements.txt /src
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

RUN python -m nltk.downloader stopwords punkt
RUN python -m manage.py makemigrations
RUN python -m manage.py migrate

COPY . /src


ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]