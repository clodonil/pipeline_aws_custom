import boto3
import botocore
import logging
import datetime
import json
import copy
import time
import os


class DyConnect:
    def __init__(self, table, region="", endpoint=""):
        self.table = table
        self.region = region
        self.endpoint = endpoint

    def connect(self):
        try:
            dydb = boto3.resource('dynamodb',region_name=self.region, endpoint_url=self.endpoint)
            conn = dydb.Table(self.table)
            return conn
        except:
            print("Problema na conexao com DynamoDB")
            logging.CRITICAL("Problema na conexao com DynamoDB")
            return False


    def dynamodb_save(self,dados,new):
        conn = self.connect()
        retorno=conn.put_item(Item=dados)


    def dynamodb_query(self, query):
        conn = self.connect()
        return conn.get_item(Key=query)
