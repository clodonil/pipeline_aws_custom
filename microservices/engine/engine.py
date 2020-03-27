from templates.pipeline_template import NewTemplate
from tools.s3 import upload_file_s3
from tools.config import filas, s3_bucket, codepipeline_roles
from tools.sqs import sqs_receive, sqs_send, sqs_delete
from daemonize import Daemonize
import json
import time

pid = "/tmp/engine.pid"

def main():
    while True:
      try:
        for event in sqs_receive(filas['processing'] ):
          make = json.loads(event.body)
          runtime = make['runtime']
          template = make['template']
          stages = make['pipeline']
          params = {}
          for param in make['Parameter']:
            params.update(param)

          # Template Base
          print("criando o template")
          pipeline = NewTemplate(template)
          file_template = pipeline.generate(runtime, 'dev', stages, template, params, roles)

          if upload_file_s3(s3_bucket, file_template):
             f_template = f"https://{s3_bucket}.s3.amazonaws.com/{file_template.split('/')[-1]}"
             msg = {"url" : f_template, "account" : "000000", "pipelinename": params['Projeto']}
             sqs_send(filas['deploy'], msg)
             sqs_delete(event)
      except:
         print('Erro ao validar')

      time.sleep(polling_time)

daemon = Daemonize(app="engine", pid=pid, action=main, foreground=True)
daemon.start()
