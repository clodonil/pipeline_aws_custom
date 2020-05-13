from tools.sqs import sqs_send
from tools.config import filas
import yaml
import uuid
import boto3
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def get_files(codecommit, repository_name, commit_id, filename):
    response = codecommit.get_file(
        repositoryName=repository_name,
        commitSpecifier=commit_id,
        filePath=filename
    )
    return response['fileContent']

def get_commit_msg(codecommit, repository_name, commit_id):
    try:
      response = codecommit.get_commit(repositoryName=repository_name,commitId=commit_id)
      msg = response['commit']['message'].replace(' ','')
      retorno = {'parents':response['commit']['parents'][0], 'msg':msg}
      return retorno
    except:
        print("Erro ao conectar no codecommit")
        return False


def change_yml_to_json(content):
    try:
        template_json = yaml.safe_load(content)
        return template_json
    except yaml.YAMLError as error:
      return  {"message": str(error)}

def add_comment(codecommit, repository, commit_id, commit_before,  msg):
    response = codecommit.post_comment_for_compared_commit(
        repositoryName=repository,
        beforeCommitId = commit_before,
        afterCommitId=commit_id,
        content=msg
    )

def lambda_handler(event, context):

   codecommit = boto3.client("codecommit")
   filepath = 'pipeline.yml'

   if 'detail' in event:
       if 'repositoryName' in event['detail'] and 'commitId' in event['detail']:
         repo = event['detail']['repositoryName']
         commit_id = event['detail']['commitId']
         account = event['account']

         retorno = get_commit_msg(codecommit, repo, commit_id)
         msg = retorno['msg']

         if 'wasabi.run()' in msg:
            print("Rodando o Wasabi")
            f_body = get_files(repo, commit_id, filepath)
            f_json = change_yml_to_json(f_body)
            if f_json['status']:
               payload = {'payload': f_json, 'account':account}
               sqs_send(filas['payload'], payload)
               msg = "Arquivo validado e enviado para o Wasabi"
               add_comment(repo, commit_id, retorno['parents'], msg)
            else:
               msg = f_json['MessageError']
               add_comment(repo, commit_id, retorno['parents'], msg)
   else:
      logging.warning("Arquivo pipeline.yml nao existe")

event = {'version': '0', 'id': 'f21d2e2c-ee13-cbce-8451-1c77388f45b6', 'detail-type': 'CodeCommit Repository State Change', 'source': 'aws.codecommit', 'account': '033921349789', 'time': '2020-03-25T12:25:58Z', 'region': 'us-east-1', 'resources': ['arn:aws:codecommit:us-east-1:033921349789:projeto'], 'detail': {'callerUserArn': 'arn:aws:iam::033921349789:user/develop', 'commitId': '91cf0fe55b6b5efd4a4a1ca716836a4e6ca0511a', 'event': 'referenceUpdated', 'oldCommitId': '34baa66383b3493507e5c626cbe0846c7b55f19a', 'referenceFullName': 'refs/heads/master', 'referenceName': 'master', 'referenceType': 'branch', 'repositoryId': 'c83c41dd-d50e-4df5-ab90-45700663cea4', 'repositoryName': 'projeto'}}
#lambda_handler(event, event)
account = event['account']
filename = '../engine/tests/payload/payload_7.yml'
#filename =  '../../tests/payload_5.yml'
#filename =  '../../tests/payload_6.yml'
f_template = open(filename)
yml_template = f_template.read()
f_template.close()
requestID = str(uuid.uuid1())
template = change_yml_to_json(yml_template)
payload = {'payload': template, 'account':account,'requestID': requestID}
print(payload)
sqs_send(filas['payload'], payload)
