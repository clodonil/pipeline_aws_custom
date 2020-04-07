from troposphere import Parameter, Ref, Template, Sub
from troposphere.s3 import Bucket, PublicRead
from troposphere.codepipeline import (
    Pipeline, Stages, Actions, ActionTypeId, OutputArtifacts, InputArtifacts,
    ArtifactStore, DisableInboundStageTransitions)


class NewPipeline:

    def create_action(self, name,runorder, configuration, type, role=""):
        config = configuration.copy()
        ListInputArtifacts = []
        if type == 'Build':
            provider = 'CodeBuild'
            category = 'Build'

            typeId=ActionTypeId(Category=category,Owner="AWS",Version="1",Provider=provider)

            inputartifact = config.pop('InputArtifacts')

            if isinstance(inputartifact, list):
               for i_artifact in inputartifact:
                   ListInputArtifacts.append(InputArtifacts(Name=i_artifact))
            else:
                ListInputArtifacts.append(InputArtifacts(Name=inputartifact))

            action = Actions(
                Name=name,
                ActionTypeId=typeId,
                InputArtifacts=ListInputArtifacts,
                OutputArtifacts=[OutputArtifacts(Name=name)],
                Configuration= config,
                RunOrder=runorder
            )

        elif type == 'Source':
            provider = 'CodeCommit'
            category = 'Source'

            typeId=ActionTypeId(Category=category,Owner="AWS",Version="1",Provider=provider)
            if role:
               action = Actions(
                 Name=name,
                 ActionTypeId=typeId,
                 OutputArtifacts=[OutputArtifacts(Name=name)],
                 Configuration=config,
                 RoleArn = role,
                 RunOrder=runorder
               )
            else:
                action = Actions(
                    Name=name,
                    ActionTypeId=typeId,
                    OutputArtifacts=[OutputArtifacts(Name=name)],
                    Configuration=config,
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
        title = name.replace('-',' ').title().replace(' ','')
        pipeline = Pipeline(
            title=title,
            Name=name,
            RoleArn=role,
            Stages=list_stages,
            ArtifactStore=ArtifactStore(Type="S3",Location=Ref(bucket_name))
        )
        return [s3bucket, pipeline]
