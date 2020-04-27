from engine import setParams
import pytest
from moto import mock_dynamodb

class TestEngine:
    @pytest.fixture
    @mock_dynamodb
    def create_dynamodb(self):
        dynamodb = boto3.resource('dynamodb')

        # Create the table
        response = dynamodb.create_table(
            TableName='cloudwatch-metrics-accounts-global',
            KeySchema=[
                {'AttributeName': 'account_id', 'KeyType': 'HASH'},  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'account_id', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print(response)


    def test_check(self):
        assert 1 == 2
#         templates = ['app-ecs']
#         return templates
#
#     @pytest.fixture
#     def payloads(self):
#         payload = [
#             'tests/payload/payload_1.yml',
#             'tests/payload/payload_2.yml',
#             'tests/payload/payload_3.yml',
#             'tests/payload/payload_4.yml',
#             'tests/payload/payload_5.yml',
#             'tests/payload/payload_6.yml',
#         ]
#         return payload
#
#
#
#     @pytest.fixture()
#     def moto_boto():
#         @mock_s3
#         def boto_resource():
#             BUCKET = 'Foo'
#             res = boto3.resource('s3')
#             res.create_bucket(Bucket=BUCKET)
#             return res
#
#         return boto_resource
#
#     @mock_s3
#     def test_with_fixture(moto_boto):
#         moto_boto()
#         client = boto3.client('s3')
#         client.list_objects(Bucket=BUCKET)
