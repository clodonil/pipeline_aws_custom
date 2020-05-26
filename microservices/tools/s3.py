"""
Tools para upload de arquivo no S3
"""

import boto3
import json
from botocore.exceptions import ClientError


def upload_file_s3(bucket, filename):
    object_name = filename.split('/')[-1]
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(filename, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_object(bucket, template):
    s3_client = boto3.client('s3')
    template_data = s3_client.get_object(Bucket=bucket,Key=template)
    template_json_data = template_data['Body'].read(template_data['ContentLength'])
    return template_json_data