"""
Microservice para deploy do template
"""
from tools.config import filas,s3_bucket
from tools.sqs import sqs_receive, sqs_delete
from tools.cloudformation import deploy
from tools.s3 import get_object
import json

while True:
  for event in sqs_receive(filas['deploy'] ):
    make = json.loads(event.body)

    # Deploy
    if deploy(make['pipelinename'], make['url']):
       sqs_delete(event)