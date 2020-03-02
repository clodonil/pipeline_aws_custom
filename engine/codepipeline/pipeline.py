from troposphere import Parameter, Ref, Template, Sub
from troposphere.s3 import Bucket, PublicRead

from troposphere.codepipeline import (
    Pipeline, Stages, Actions, ActionTypeId, OutputArtifacts, InputArtifacts,
    ArtifactStore, DisableInboundStageTransitions)




class NewPipeline:
        
    def create_action(self, name,runorder, configuration, type):
        config = configuration.copy()
        if type == 'Build':
           provider = 'CodeBuild'
           category = 'Build'
           
           typeId=ActionTypeId(Category=category,Owner="AWS",Version="1",Provider=provider)
           
           action = Actions(
                Name=name,
                ActionTypeId=typeId,
                InputArtifacts=[InputArtifacts(Name=config.pop('InputArtifacts'))],
                OutputArtifacts=[OutputArtifacts(Name=name)],
                Configuration= configuration,
                RunOrder=runorder
            )

        elif type == 'Source':
             provider = 'CodeCommit'
             category = 'Source'
           
             typeId=ActionTypeId(Category=category,Owner="AWS",Version="1",Provider=provider)
             action = Actions(
                 Name=name,
                 ActionTypeId=typeId,                 
                 OutputArtifacts=[OutputArtifacts(Name=name)],
                 Configuration= config,
                 RunOrder=runorder
            )
        return action        

    def create_stage(self, name, list_actions):
        stage = Stages (
            Name = name,
            Actions = list_actions
        )
        return stage


    def create_pipeline(self, name, role, list_stages):

        bucket_name = "PipelinePythonReports"

        s3bucket = Bucket(bucket_name)

        pipeline = Pipeline(
            name,            
            RoleArn=role,
            Stages = list_stages,
            ArtifactStore=ArtifactStore(Type="S3",Location=Ref(bucket_name))
        )

        return [s3bucket, pipeline]

