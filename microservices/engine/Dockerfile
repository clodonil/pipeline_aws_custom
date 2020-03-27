FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"

ENV VPCID='vpc-bb0436c1'
ENV SUBNET_A='subnet-035ab95c'
ENV SUBNET_B='subnet-4c518942'
ENV SECGROUP='sg-56391a7c'

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["/bin/bash", "-c", "python engine.py"]
