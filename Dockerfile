FROM python:3.9-alpine

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . src
WORKDIR /src

EXPOSE 8000

ENTRYPOINT [ "python" ]
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]