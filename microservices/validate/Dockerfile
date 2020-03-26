FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["/bin/bash", "-c", "python3 validate.py"]
