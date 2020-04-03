"""
Microservice para deploy do template
"""
from tools.config import filas, s3_bucket, polling_time
from tools.sqs import sqs_receive, sqs_delete
from tools.cloudformation import deploy
from tools.s3 import get_object
from daemonize import Daemonize
import json
import time

pid = "/tmp/deploy.pid"

def main():
  while True:
    #try:
      for event in sqs_receive(filas['deploy'] ):
        make = json.loads(event.body)

        # Deploy
        if deploy(make):
           sqs_delete(event)
    #except:
    #    print("erro no deploy")
      time.sleep(polling_time)

#daemon = Daemonize(app="deploy", pid=pid, action=main, foreground=True)
#daemon.start()
main()
