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
            self.conn = dydb.Table(self.table)
            return self.conn
        except:
            print("Problema na conexao com DynamoDB")
            logging.CRITICAL("Problema na conexao com DynamoDB")
            return False


    def dynamodb_save(self,dados,new):
        conn = self.connect()
        retorno=conn.put_item(Item=dados)
        print(retorno)


    def dynamodb_query(self,table,query):
        return table.get_item(Key=query)


if __name__ == "__main__":

   template = { 'name' : 'app-ecs',
                'details' : {
                             '1-source'   : [],
                             '2-ci'       : [
                                               {'Sast':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App', 'runorder': '1'}}, 
                                               {'Sonar':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1'}}, 
                                               {'TestUnit':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1'}}, 
                                               {'Build':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1'}}
                                               ],
                             '3-security' : [
                                              {'Aqua': {'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1' }}
                                            ],
                             '4-publish'  : [
                                              {'PublishECR':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1' }}
                                            ],
                             '5-deploy'   : [
                                              {'DeployECS':{'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App','runorder': '1' }}
                                            ]
                           }
   }

   print(template)
   newtemplate = DyConnect('pipeline-custom-templates','us-east-1', 'http://localhost:4569')
   newtemplate.dynamodb_save(template, True)




       


