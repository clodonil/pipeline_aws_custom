import boto3
import json
from tools.config import aws_region


def sqs_receive(fila):
    """
    recupera templates da lista
    """
    sqs = boto3.resource('sqs', region_name=aws_region)
    conn = sqs.get_queue_by_name(QueueName=fila)
    messages = conn.receive_messages(MaxNumberOfMessages=10, AttributeNames=[
                                     'All'], WaitTimeSeconds=1)
    return messages


def sqs_send(fila, msg):
    """
     envia mensagem para lista
    """
    sqs = boto3.resource('sqs', region_name=aws_region)
    conn = sqs.get_queue_by_name(QueueName=fila)
    retorno = conn.send_message(MessageBody=json.dumps(msg))
    return retorno


def sqs_delete(event):
    """
    deletando mensagem da fila
    """
    try:
        retorno = event.delete()
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except:
        return False
