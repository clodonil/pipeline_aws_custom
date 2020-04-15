from templates.pipeline_template import NewTemplate
from tools.s3 import upload_file_s3
from tools.config import (filas, s3_bucket, RoleCodePipeline,
                          RoleCodeBuild, polling_time, DevSecOps_Role)
from tools.sqs import sqs_receive, sqs_send, sqs_delete
from tools.dynamodb import get_dy_template, get_sharedlibrary_release
from daemonize import Daemonize
import json
import time
import os


pid = "/tmp/engine.pid"


def main():
    while True:
     #   try:
            for event in sqs_receive(filas['processing']):
                print("Consumindo mensagem")
                payload = json.loads(event.body)
                requestID = payload['requestID']
                account = payload['account']
                make = payload['payload']
                runtime = make['runtime']
                template = make['template']
                stages = make['pipeline']
                params = {}
                for param in make['Parameter']:
                    params.update(param)

                # Template Base
                print("criando o template")
                codebuild_role = f'arn:aws:iam::{account}:role/{RoleCodeBuild}'
                codepipeline_roles = f'arn:aws:iam::{account}:role/{RoleCodePipeline}'

                pipeline_stages = get_dy_template(template)
                release = get_sharedlibrary_release()

                pipeline = NewTemplate(template, codepipeline_roles, codebuild_role, DevSecOps_Role)
                file_template = pipeline.generate(runtime, 'dev', stages, pipeline_stages, params, account, release)

                if upload_file_s3(s3_bucket, file_template):
                    f_tp = file_template.split('/')[-1]
                    f_template = f"https://{s3_bucket}.s3.amazonaws.com/{f_tp}"
                    msg = {
                        "url": f_template,
                        "account": account,
                        "pipelinename": params['Projeto'],
                        'requestID': requestID
                    }
                    sqs_send(filas['deploy'], msg)
                    sqs_delete(event)
        #         try:
        #             os.remove(file_template)
        #         except IOError as error:
        #             print(error)
        # except NameError as error:
        #     print('Erro ao validar', str(error))
        # time.sleep(polling_time)
#daemon = Daemonize(app="engine", pid=pid, action=main, foreground=True)
#daemon.start()
main()
