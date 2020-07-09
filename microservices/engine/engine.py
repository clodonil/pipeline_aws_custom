from templates.pipeline_template import NewTemplate
from tools.s3 import upload_file_s3
from tools.config import (filas, s3_bucket, RoleCodePipeline,
                          RoleCodeBuild, polling_time, DevSecOps_Role)
from tools.sqs import sqs_receive, sqs_send, sqs_delete
from tools.dynamodb import get_dy_template, get_sharedlibrary_release, get_imageCustom
from daemonize import Daemonize
import json
import time
import sys
from tools.log import logger, WasabiLog

pid = "/tmp/engine.pid"


def setParams(payload, env):
    template = payload['payload']['template']
    dynamodb_template = get_dy_template(template)
    logger.info(f"Lendo template da pipeline do dynamodb")
    pipeline_stages = dynamodb_template.get('pipeline')
    estrutura = dynamodb_template.get('structure')
    dependencias = dynamodb_template.get('depends')
    release = get_sharedlibrary_release()
    imageCustom = get_imageCustom()
    params = {}
    for param in payload['payload']['Parameter']:
        params.update(param)
    template_params = {
        'env': env,
        'runtime': payload['payload']['runtime'],
        'stages': payload['payload']['pipeline'][env],
        'account': payload['account'],
        'pipeline_stages': pipeline_stages,
        'params': params,
        'release': release,
        'imageCustom': imageCustom,
        'type': template,
        'structure': estrutura,
        'depends': dependencias
    }
    logger.info(f'Parametros definidos para criacao do template')
    return template_params


def save_s3_send_sqs(template_params, requestID, file_template, event):
    bucket = s3_bucket.split('.')[0].replace('https://', '')
    logger.info(f'Enviando template para o bucket {bucket}')
    if upload_file_s3(bucket, file_template):
        f_tp = file_template.split('/')[-1]
        f_template = f"{s3_bucket}{f_tp}"
        msg = {
            "url": f_template,
            "account": template_params['account'],
            "pipelinename": template_params['params']['Projeto'],
            "requestID": requestID
        }
        logger.info(
            f"Mensagem Enviada para Fila: {filas['deploy']}, RequestId: {msg['requestID']}")
        logger.info(f"Mensagem: {msg}")
        sqs_send(filas['deploy'], msg)


def process_templates():
    for event in sqs_receive(filas['processing']):
        payload = json.loads(event.body)
        requestID = payload['requestID']
        logger.info(f'Event: {event.body}')

        # Template Base
        codebuild_role = f"arn:aws:iam::{payload['account']}:role/{RoleCodeBuild}"
        codepipeline_roles = f"arn:aws:iam::{payload['account']}:role/{RoleCodePipeline}"
        for envs in payload['payload']['pipeline'].keys():
            template_params = setParams(payload, envs)
            pipeline = NewTemplate(
                codepipeline_roles, codebuild_role, DevSecOps_Role)
            file_template = pipeline.generate(tp=template_params)
            logger.info(f'Template gerado com sucesso')
            save_s3_send_sqs(template_params, requestID,
                             file_template, event)
            logger.info(
                f"Deletando Mensagem da Fila: {filas['processing']}, RequestId: {requestID}")
            sqs_delete(event)
        return file_template


if __name__ == "__main__":
    def main():
        while True:
            try:
                process_templates()
            except Exception as error:
                logger.warning(f'Error: {error}')
            time.sleep(polling_time)
    daemon = Daemonize(app="engine", pid=pid, action=main, foreground=True)
    daemon.start()
