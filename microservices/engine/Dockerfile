FROM python:3.8-alpine as base

RUN apk update && apk add build-base gcc libressl-dev musl-dev libffi-dev

COPY . /app
WORKDIR /app

RUN pip install --user -r requirements.txt

FROM base

COPY --from=builder /app /app
COPY --from=builder /root/.local /root/.local

WORKDIR /app
CMD ["/bin/bash", "-c", "python engine.py"]
