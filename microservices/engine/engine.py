from templates.pipeline_template import NewTemplate
from tools.s3 import upload_file_s3
from tools.config import (filas, s3_bucket, RoleCodePipeline,
                          RoleCodeBuild, polling_time, DevSecOps_Role)
from tools.sqs import sqs_receive, sqs_send, sqs_delete
from tools.dynamodb import get_dy_template, get_sharedlibrary_release, get_imageCustom
from daemonize import Daemonize
import json
import time
import os


pid = "/tmp/engine.pid"


def setParams(payload, env):
    template = payload['payload']['template']
    pipeline_stages = get_dy_template(template)
    release = get_sharedlibrary_release()
    imageCustom = get_imageCustom()
    params = {}
    for param in payload['payload']['Parameter']:
        params.update(param)
    template_params = {
        'env': env,
        'runtime': payload['payload']['runtime'],
        'stages': payload['payload']['pipeline'],
        'account': payload['account'],
        'pipeline_stages': pipeline_stages[env],
        'params': params,
        'release': release,
        'imageCustom': imageCustom
    }
    return template_params

def save_s3_send_sqs(template_params, requestID, file_template, event):
    bucket = s3_bucket.split('.')[0].replace('https://','')
    if upload_file_s3(bucket, file_template):
       f_tp = file_template.split('/')[-1]
       f_template = f"{s3_bucket}{f_tp}"
       msg = {
           "url": f_template,
           "account": template_params['account'],
           "pipelinename": template_params['params']['Projeto'],
           "requestID": requestID
       }
       print("Mensagem Enviada para para Fila de Deploy")
       #sqs_send(filas['deploy'], msg)
       print("Deletando a mensagem da fila de processamento")
       #sqs_delete(event)

def main():
    while True:
     #   try:
            for event in sqs_receive(filas['processing']):
                print("Consumindo mensagem")
                payload = json.loads(event.body)
                requestID = payload['requestID']

                # Template Base
                print("criando o template")
                codebuild_role = f"arn:aws:iam::{payload['account']}:role/{RoleCodeBuild}"
                codepipeline_roles = f"arn:aws:iam::{payload['account']}:role/{RoleCodePipeline}"
                template_params = setParams(payload, 'develop')
                pipeline = NewTemplate(codepipeline_roles, codebuild_role, DevSecOps_Role)
                file_template = pipeline.generate(tp=template_params)
                print("Enviando o template para o Bucket")
                save_s3_send_sqs(template_params, requestID,file_template, event)

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
