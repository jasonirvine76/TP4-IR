FROM python:3.9-alpine

EXPOSE 8000
WORKDIR /src

COPY requirements.txt /src
RUN pip install -r requirements.txt --no-cache-dir

COPY . /src


ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]