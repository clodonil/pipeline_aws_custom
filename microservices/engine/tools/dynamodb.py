"""
Tools de integração com o Dynamodb
"""
import boto3
import botocore
import logging
import datetime
import json
import copy
import time
import os
from tools.config import dynamodb, aws_region

class DyConnect:
    def __init__(self, table, region):
        self.table = table
        self.region = region

    def connect(self):
        try:
            dydb = boto3.resource('dynamodb', region_name=self.region)
            conn = dydb.Table(self.table)
            return conn
        except:
            print("Problema na conexao com DynamoDB")
            logging.CRITICAL("Problema na conexao com DynamoDB")
            return False

    def dynamodb_save(self, dados):
        conn = self.connect()
        if conn:
           retorno = conn.put_item(Item=dados)

    def dynamodb_query(self, query):
        conn = self.connect()
        return conn.get_item(Key=query)


def get_dy_template(template_name):
    newtemplate = DyConnect(dynamodb['template'], aws_region)
    query = {'name': template_name}
    stages = newtemplate.dynamodb_query(query)

    if 'Item' in stages:
        if 'details' in stages['Item']:
            return stages['Item']['details']

    return False

def get_sharedlibrary_release():
    newtemplate = DyConnect(dynamodb['template'], aws_region)
    query = {'name': 'sharedlibrary'}
    version = newtemplate.dynamodb_query(query)

    if 'Item' in version:
        return version['Item']['release']
    return False

def get_imageCustom():
    newtemplate = DyConnect(dynamodb['template'], aws_region)
    query = {'name': 'imagecustom'}
    version = newtemplate.dynamodb_query(query)

    if 'Item' in version:
        return version['Item']['details']
    return False

