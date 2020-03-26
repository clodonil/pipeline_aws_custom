from microservices.tools.sqs import sqs_send
from microservices.tools.config import filas
import yaml
import boto3

def get_files(repository_name, commit_id, filename):
    codecommit = boto3.client("codecommit")
    response = codecommit.get_file(
        repositoryName=repository_name,
        commitSpecifier=commit_id,
        filePath=filename
    )
    return response['fileContent']

def get_commit_msg(repository_name, commit_id):
    codecommit = boto3.client("codecommit")
    response = codecommit.get_commit(repositoryName=repository_name,commitId=commit_id)
    msg = response['commit']['message'].replace(' ','')
    return msg

def change_yml_to_json(ftemplate):
    with open(ftemplate, 'r') as stream:
        try:
           template_json = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
           return  {"message":"Erro ao processar arquivo yml"}
        return template_json

def add_comment(commit_id, msg):
    codecommit = boto3.client("codecommit")
    response = codecommit.update_comment(commentId=commit_id,content=msg)
    print(response)


def lambda_handler(event, context):
   repo = event['detail']['repositoryName']
   commit_id = event['detail']['commitId']
   filepath = 'pipeline.yml'

   msg = get_commit_msg(repo, commit_id)
   if 'wasabi.run()' in msg:
      print("Rodando o Wasabi")
      f_body = get_files(repo, commit_id, filepath)
      try:
        f_json = yaml.safe_load(f_body)
        sqs_send(filas['payload'], f_json)
        msg = "Wasabi rodando"
        add_comment(commit_id, msg)
      except:
        msg = "Problema ao processar o arquivo da pipeline.yml"
        add_comment(commit_id, msg)


#event = {'version': '0', 'id': 'f21d2e2c-ee13-cbce-8451-1c77388f45b6', 'detail-type': 'CodeCommit Repository State Change', 'source': 'aws.codecommit', 'account': '033921349789', 'time': '2020-03-25T12:25:58Z', 'region': 'us-east-1', 'resources': ['arn:aws:codecommit:us-east-1:033921349789:projeto'], 'detail': {'callerUserArn': 'arn:aws:iam::033921349789:user/develop', 'commitId': '91cf0fe55b6b5efd4a4a1ca716836a4e6ca0511a', 'event': 'referenceUpdated', 'oldCommitId': '34baa66383b3493507e5c626cbe0846c7b55f19a', 'referenceFullName': 'refs/heads/master', 'referenceName': 'master', 'referenceType': 'branch', 'repositoryId': 'c83c41dd-d50e-4df5-ab90-45700663cea4', 'repositoryName': 'projeto'}}
#lambda_handler(event, event)

#filename = '../../tests/payload.yml'
filename =  '../../tests/payload_custom1.yml'
#filename =  '../../tests/payload_custom2.yml'

template = change_yml_to_json(filename)
sqs_send(filas['payload'], template)
