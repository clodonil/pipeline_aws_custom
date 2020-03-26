from microservices.tools.dynamodb import DyConnect
from microservices.tools.config import dynamodb, aws_region
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


   table = dynamodb['template']
   newtemplate = DyConnect(table,aws_region)
   newtemplate.dynamodb_save(template)
