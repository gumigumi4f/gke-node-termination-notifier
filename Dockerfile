FROM python:3.9-slim as builder

WORKDIR /gkentn

COPY pyproject.toml poetry.lock /gkentn/
COPY src /gkentn/src/

RUN pip3 install -U pip \
      && pip3 install poetry \
      && poetry build -f wheel

FROM python:3.9-alpine

WORKDIR /gkentn

COPY --from=builder /gkentn/dist /wheels

RUN pip3 install -U pip \
      && pip3 install gke-node-termination-notifier -f /wheels \
      && pip3 cache purge

ENTRYPOINT [ "gkentn" ]
