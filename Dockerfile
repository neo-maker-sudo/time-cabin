# first stage output poetry dependencies list into requirements.txt
FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY poetry.lock pyproject.toml /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# second stage install dependencies library, and others deploy configuration file
FROM python:3.10

# create user, option -m means create home directory, -s means login shell
# https://stackoverflow.com/questions/27701930/how-to-add-users-to-docker-container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PROJECT_HOME=/home/web/m3u8
ENV TZ="Asia/Taipei"

RUN useradd -ms /bin/bash web \
    && mkdir -p $PROJECT_HOME \ 
    && mkdir -p /var/log/gunicorn/error \
    && mkdir -p /var/log/gunicorn/access \
    && chown -R web:web /var/log/gunicorn

WORKDIR $PROJECT_HOME

COPY --from=requirements-stage /tmp/requirements.txt $PROJECT_HOME/requirements.txt

RUN pip install --no-cache-dir --upgrade -r $PROJECT_HOME/requirements.txt

COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends vim supervisor \
    && cp ./supervisord/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./supervisord/entrypoint.sh .
RUN chmod +x ./supervisord/entrypoint.sh