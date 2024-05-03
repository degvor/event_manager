FROM python:3.9-alpine3.13
LABEL maintainer="degvor"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev

COPY requirements.txt requirements.dev.txt /app/
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    /py/bin/pip install -r requirements.dev.txt

RUN apk del .tmp-build-deps

COPY . /app

EXPOSE 8000

ENV PATH="/py/bin:$PATH"

RUN adduser --disabled-password --no-create-home django-user
USER django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
