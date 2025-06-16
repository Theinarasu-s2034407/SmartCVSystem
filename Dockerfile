FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev python3-dev build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir mysqlclient --only-binary :alla: && pip install --no-cache-dir -r requirements.txt

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh


COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]