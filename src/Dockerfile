FROM python:3.13-slim as BUILD

WORKDIR /temp

RUN pip install uv

COPY ./pyproject.toml /temp/pyproject.toml
COPY ./uv.lock /temp/uv.lock

RUN uv export --format requirements.txt -o requirements.txt --no-cache

FROM python:3.13-slim 

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src

COPY --from=BUILD /temp/requirements.txt /usr/src/requirements.txt

RUN pip install --no-cache-dir -r /usr/src/requirements.txt

COPY . /usr/src

CMD [ "fastapi", "run", "--port", "8000" ]