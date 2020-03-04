import logging
import boto3
from botocore.exceptions import ClientError


def upload_file_s3(filename):
    bucket = 'pipeline-custom-templates'
    object_name = filename.split('/')[1]
    endpoint = 'http://localhost:4572'


    # Upload the file
    s3_client = boto3.client('s3', endpoint_url=endpoint)
    try:
        response = s3_client.upload_file(filename, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    print(response)
    return True