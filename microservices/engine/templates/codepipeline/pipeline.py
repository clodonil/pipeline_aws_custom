from troposphere import Ref, Sub
from troposphere.codepipeline import (
    Pipeline, Stages, Actions, ActionTypeId, OutputArtifacts, InputArtifacts,
    ArtifactStore, EncryptionKey)
from tools.log import WasabiLog


class NewPipeline:

    @WasabiLog
    def create_action(self, name, runorder, configuration, type, role=""):
        project_name = ''.join(e for e in name if e.isalnum())
        config = configuration.copy()
        ListInputArtifacts = []
        action = None
        if type == 'CodeBuild':
            provider = 'CodeBuild'
            category = 'Build'

            typeId = ActionTypeId(
                Category=category,
                Owner="AWS",
                Version="1",
                Provider=provider)

            inputartifact = config.pop('InputArtifacts')

            if isinstance(inputartifact, list):
                for i_artifact in inputartifact:
                    ListInputArtifacts.append(InputArtifacts(Name=i_artifact))
            else:
                ListInputArtifacts.append(InputArtifacts(Name=inputartifact))

            action = Actions(
                project_name,
                Name=name,
                ActionTypeId=typeId,
                InputArtifacts=ListInputArtifacts,
                OutputArtifacts=[OutputArtifacts(Name=name)],
                Configuration=config,
                RunOrder=runorder
            )

        elif type == 'Source':
            provider = 'CodeCommit'
            category = 'Source'
            if 'OutputArtifacts' in configuration:
                outputartifacts = config.pop('OutputArtifacts')
            else:
                outputartifacts = project_name

            typeId = ActionTypeId(
                Category=category,
                Owner="AWS",
                Version="1",
                Provider=provider
            )
            if role:
                action = Actions(
                    project_name,
                    Name=name,
                    ActionTypeId=typeId,
                    OutputArtifacts=[OutputArtifacts(Name=outputartifacts)],
                    Configuration=config,
                    RoleArn=role,
                    RunOrder=runorder
                )
            else:
                action = Actions(
                    project_name,
                    Name=name,
                    ActionTypeId=typeId,
                    OutputArtifacts=[OutputArtifacts(Name=outputartifacts)],
                    Configuration=config,
                    RunOrder=runorder
                )
        elif type == 'Approval':

            typeId = ActionTypeId(
                Category='Approval',
                Owner="AWS",
                Version="1",
                Provider='Manual'
            )

            action = Actions(
                project_name,
                Name=name,
                ActionTypeId=typeId,
                Configuration=config,
                RunOrder=runorder
            )
        elif type == 'InvokeLambda':
            inputartifact = config.pop('InputArtifacts')
            rolearn = config.pop('RoleArn')
            typeId = ActionTypeId(
                Category='Invoke',
                Owner='AWS',
                Provider='Lambda',
                Version='1',
            )
            action = Actions(
                project_name,
                Name=name,
                ActionTypeId=typeId,
                Configuration=config,
                InputArtifacts=inputartifact,
                RoleArn=rolearn,
                RunOrder=runorder
            )

        return action

    @WasabiLog
    def create_stage(self, name, list_actions):
        project_name = ''.join(e for e in name if e.isalnum())
        stage = Stages(
            project_name,
            Name=name,
            Actions=list_actions
        )
        return stage

    @WasabiLog
    def create_pipeline(self, name, role, list_stages):
        # bucket_name = f"{name}-reports"
        # project_name = ''.join(e for e in bucket_name if e.isalnum())

        title = name.replace('-', ' ').title().replace(' ', '')
        encrypt = EncryptionKey(Id=Ref('KMSKeyArn'), Type='KMS')
        pipeline = Pipeline(
            title=title,
            Name=name,
            RoleArn=role,
            Stages=list_stages,
            ArtifactStore=ArtifactStore(
                Type="S3",
                Location=Sub('${AWS::AccountId}-artefatos'),
                EncryptionKey=encrypt
            )
        )
        return [pipeline]
