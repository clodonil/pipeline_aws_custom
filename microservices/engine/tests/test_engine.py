# from engine import setParams
# from engine import process_templates
import engine
from tools.config import filas, dynamodb
from tools.sqs import sqs_send, sqs_receive
from tools.dynamodb import DyConnect
from tools.config import dynamodb, aws_region, s3_bucket
from tools.validates import change_yml_to_json
from tools.s3 import get_object
from moto import mock_dynamodb2, mock_sqs, mock_s3
import pytest
import boto3
import json


class TestEngine:

    @mock_s3
    def create_bucket(self):
        s3 = boto3.client('s3')
        bucket = s3_bucket.split('.')[0].replace('https://', '')
        s3.create_bucket(Bucket=bucket)
        return s3

    @mock_sqs
    def create_sqs(self):
        sqs = boto3.resource('sqs')
        queue = sqs.create_queue(QueueName=filas['processing'], Attributes={
                                 'DelaySeconds': '1', 'VisibilityTimeout': '360'})
        queue = sqs.create_queue(QueueName=filas['deploy'], Attributes={
                                 'DelaySeconds': '1'})

        return queue

    @mock_dynamodb2
    def create_dynamodb(self):
        dy = boto3.resource('dynamodb')
        table = dynamodb['template']
        table = dy.create_table(
            TableName=table,
            KeySchema=[
                {'AttributeName': 'name',
                 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'name',
                 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10
            }
        )
        return table

    @mock_dynamodb2
    def carga_do_template_da_pipeline_na_tabela_dynamodb(self):
        self.create_dynamodb()
        imagemcustom = {
            "details": {
                "Aqua": {
                    "all": "imagem_Aqua"
                },
                "Build": {
                    "all": "image_Build_default",
                    "python37": "image_custom_python37"
                },
                "Fortify": {
                    "all": "imagem_sast_defaul"
                },
                "Sonar": {
                    "all": "imagem_sonar_default"
                },
                "TestUnit": {
                    "all": "imagem_TestUnit"
                }
            },
            "name": "imagecustom"
        }
        sharedlibrary = {
            "name": "sharedlibrary",
            "release": "release-1"
        }

        table = dynamodb['template']
        newtemplate = DyConnect(table, aws_region)
        payloads = ['payload-ecs']
        for payload in payloads:
            filename = f"tests/{payload}/templates.json"
            f_template = open(filename)
            template_json = f_template.read()
            f_template.close()
            newtemplate.dynamodb_save(json.loads(template_json))
        newtemplate.dynamodb_save(imagemcustom)
        newtemplate.dynamodb_save(sharedlibrary)

    @mock_s3
    @mock_sqs
    def test_carga_dos_templates_no_sqs(self):
        self.create_sqs()
        s3 = self.create_bucket()
        self.carga_do_template_da_pipeline_na_tabela_dynamodb()
        bucket = s3_bucket.split('.')[0].replace('https://', '')
        payloads = ['payload-ecs']
        payload_files = [
            'payload_1.yml',
            'payload_2.yml',
            'payload_3.yml',
            'payload_4.yml',
            'payload_5.yml',
            'payload_6.yml'
        ]

        for payload in payloads:
            for filename in payload_files:
                path_filename = f"tests/{payload}/{filename}"
                f_template = open(path_filename)
                yml_template = f_template.read()
                f_template.close()
                json_template = change_yml_to_json(yml_template)
                send_payload = {'payload': json_template,
                                'requestID': 'xxxx-xxxx-xxxx', 'account': filename}
                sqs_send(filas['processing'], send_payload)

                # criar a pipeline
                template_name = engine.process_templates()

                # Verificando se o template foi criado no bucket
                lista_pipelines = [
                    'Pipeline-Python-develop-payload_1.yml.json',
                    'Pipeline-Python-develop-payload_2.yml.json',
                    'Pipeline-Python-develop-payload_3.yml.json',
                    'Pipeline-Python-develop-payload_4.yml.json',
                    'Pipeline-Python-develop-payload_5.yml.json',
                    'Pipeline-Python-develop-payload_6.yml.json',
                    'Pipeline-Python-master-payload_1.yml.json'
                ]
                s3 = boto3.resource('s3')
                my_bucket = s3.Bucket(bucket)
                for object_summary in my_bucket.objects.filter():
                    print("=====>", object_summary.key)
                    assert object_summary.key in lista_pipelines
