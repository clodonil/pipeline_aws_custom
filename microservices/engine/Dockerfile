FROM python:3.7-alpine as base

#RUN apk update && apk add build-base gcc

COPY . /app
WORKDIR /app

RUN pip install --user -r requirements.txt

FROM base

COPY --from=builder /app /app
COPY --from=builder /root/.local /root/.local

WORKDIR /app
CMD ["/bin/bash", "-c", "python engine.py"]
