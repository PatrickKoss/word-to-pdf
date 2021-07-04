FROM python:3.9.6-slim
RUN apt-get clean && apt-get -y update
RUN apt-get update && apt-get -y install gcc
RUN mkdir -p /usr/share/man/man1
RUN apt-get update && apt-get -y -q install libreoffice
WORKDIR /app
COPY requirements/requirements_linux.txt ./
RUN pip install --no-cache-dir -r requirements_linux.txt
COPY app.py .
COPY wsgi.py .
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEVELOPMENT "false"
ENV LIBRE_OFFICE_PATH "soffice"
EXPOSE 5000
CMD gunicorn --workers 4 --bind 0.0.0.0:5000 app:api --log-level info