FROM python:3.10.4-slim-bullseye

COPY ./requirements /requirements
COPY ./scripts /scripts
COPY ./src /src

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR src

EXPOSE 8000

RUN pip install -r /requirements/development.txt

RUN chmod -R +x /scripts && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    adduser --disabled-password --no-create-home b2b && \
    chown -R b2b:b2b /vol && \
    chmod -R 755 /vol


ENV PATH="/scripts:$PATH"

USER b2b

CMD ["run.sh"]