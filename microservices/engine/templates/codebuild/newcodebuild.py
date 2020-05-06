

from troposphere.codebuild import (
    Artifacts, Environment, Source, Project, VpcConfig, ProjectCache)
from troposphere import Ref, Sub
from tools.config import version


class NewCodeBuild:
    def __init__(self, roleCodeBuild):
        self.roleCodeBuild = roleCodeBuild
        self.kMSKeyArn = Ref('KMSKeyArn')
        self.vpcid = Ref("VPCID")
        self.privatesubnetOne = Ref("PrivateSubnetOne")
        self.privatesubnetTwo = Ref("PrivateSubnetTwo")
        self.sgpipeline = Ref("SG")
        self.computeType = 'BUILD_GENERAL1_SMALL'
        self.image = 'aws/codebuild/standard:2.0'
        self.type = 'LINUX_CONTAINER'
        self.artifacts = Artifacts(Type='CODEPIPELINE')
        self.vpcConfig = VpcConfig(
            VpcId=self.vpcid,
            Subnets=[self.privatesubnetOne, self.privatesubnetTwo],
            SecurityGroupIds=[self.sgpipeline]
        )
        self.timeoutInMinutes = 10

    def create_codebuild(self, title, name, envs, imagecustom=False, buildspec=False,cache=True):
        project_name = title
        # imagem do codebuild
        if imagecustom:
            dockerimage = imagecustom
            serviceRole = "SERVICE_ROLE"
        else:
            dockerimage = self.image
            serviceRole = "CODEBUILD"

        # Path do codebuild
        if buildspec:
            pathBuildSpec = f'{buildspec}'
        else:
            pathBuildSpec = f'pipeline/buildspec_{name.lower()}.yml'

        if isinstance(envs, list):
            if all(isinstance(env, dict) for env in envs):
                for env in envs:
                    if 'Name' in env and 'Value' in env:
                        envs = envs
                    else:
                        envs = []
            else:
                envs = []
        else:
            envs = []

        environment = Environment(
            ComputeType=self.computeType,
            Image=dockerimage,
            Type=self.type,
            EnvironmentVariables=envs,
            PrivilegedMode='true',
            ImagePullCredentialsType = serviceRole
        )

        source = Source(
            BuildSpec=pathBuildSpec,
            Type='CODEPIPELINE'
        )

        if cache:
            use_cache = ProjectCache(
                Location = Sub('${AWS::AccountId}-cache'),
                Type = 'S3',
                Modes = ['LOCAL_CUSTOM_CACHE']
            )
            codebuild = Project(
                project_name,
                Artifacts=self.artifacts,
                Environment=environment,
                Name=name,
                ServiceRole=self.roleCodeBuild,
                Source=source,
                EncryptionKey=self.kMSKeyArn,
                TimeoutInMinutes=self.timeoutInMinutes,
                Cache=use_cache,
                VpcConfig=self.vpcConfig
            )
        else:
            codebuild = Project(
                project_name,
                Artifacts=self.artifacts,
                Environment=environment,
                Name=name,
                ServiceRole=self.roleCodeBuild,
                Source=source,
                EncryptionKey=self.kMSKeyArn,
                TimeoutInMinutes=self.timeoutInMinutes,
                VpcConfig=self.vpcConfig
            )
        return codebuild

    def ImageCustom(self, title, imagecustom, runtime):
        if title in imagecustom:
            image = imagecustom[title][runtime] if runtime in imagecustom[title] else imagecustom[title]['all']
        else:
            image = False
        return image

    def ControlVersion(self, **params):
        # TODO: PIPELINETYPE requerer uma variável App

        env = [
            {
                "Name": 'QUEUE',
                "Value": 'https://sqs.sa-east-1.amazonaws.com/049557819541/codemetrics'
            },
            {
                "Name" : 'RUNTIME',
                "Value" : params['runtime']
            },
            {
                "Name": 'PIPELINETYPE',
                "Value": params['runtime']
            },
            {
                "Name": 'VERSION',
                "Value": f'Wasabi-{version}'
            }
        ]
        title = 'ControlVersion'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-ControlVersion-{params['branchname']}"
        controlversion = self.create_codebuild('ControlVersion', name.lower(), env, image, f'common/controlversion/buildspec.yml')
        return controlversion

    def Fortify(self, **params):
        env =[
            {
                'Name' : 'BranchName',
                'Value': params['branchname']

            },
            {
                'Name': 'VariablePath',
                'Value': f"/App/{params['featurename']}/{params['microservicename']}/"
            },
            {
                'Name': 'AccountID',
                'Value': '!Sub ${AWS::AccountId}'
            },
            {
                'Name': 's3bucket',
                'Value': '!Sub ${AWS::AccountId}-reports'
            },
            {
                'Name': 'queue',
                'Value': 'https://sqs.sa-east-1.amazonaws.com/049557819541/DevSecOps-ToolsReports'
            },
            {
                'Name': 'microservicename',
                'Value': params['microservicename']
            },
            {
                'Name': 'featurename',
                'Value': params['featurename']
            }
        ]
        title = 'Fortify'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Fortify-{params['branchname']}"
        runtime_path = '/'.join(params['runtime'].split(':'))
        buildspec = f"../01/{runtime_path}/sast/buildspec.yml"
        sast = self.create_codebuild(title, name.lower(), env, image, buildspec)
        return sast

    def Sonar(self, **params):
        env = [
            {
                'Name': 'BranchName',
                'Value': params['branchname']
            },
            {
                'Name': 's3bucket',
                'Value': '!Sub ${AWS::AccountId}-reports'
            },
            {
                'Name': 'microservicename',
                'Value': params['microservicename']
            },
            {
                'Name': 'featurename',
                'Value': params['featurename']
            }
        ]
        title = 'Sonar'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Sonar-{params['branchname']}"
        runtime_path = '/'.join(params['runtime'].split(':'))
        buildspec = f"../01/{runtime_path}/sonarqube/buildspec.yml"
        sonar = self.create_codebuild(title, name.lower(), env, image, buildspec)
        return sonar

    def TestUnit(self, **params):
        env = [
            {
                'Name': 'DevSecOpsAccount',
                'Value': '!Ref DevSecOpsAccount'
            }
        ]
        if params['custom']:
            buildspec = "pipeline/buildspec_testunit.yml"
        else:
            runtime_path = '/'.join(params['runtime'].split(':'))
            buildspec = f"../01/{runtime_path}/testunit/buildspec.yml"

        title = 'TestUnit'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-TestUnit-{params['branchname']}"
        testunit = self.create_codebuild(title, name.lower(), env, image, buildspec)
        return testunit

    def Build(self, **params):
        env = [
            {
                'Name': 'DevSecOpsAccount',
                'Value': '!Ref DevSecOpsAccount'
            }
        ]
        if params['custom']:
            buildspec = "pipeline/buildspec_build.yml"
        else:
            runtime_path = '/'.join(params['runtime'].split(':'))
            buildspec = f"../01/{runtime_path}/build/buildspec.yml"

        title = 'Build'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Build-{params['branchname']}"
        build = self.create_codebuild(title, name.lower(), env, image, buildspec)
        return build

    def Aqua(self, **params):
        env =[
            {
                'Name' : 'BranchName',
                'Value': params['branchname']

            },
            {
                'Name': 'VariablePath',
                'Value': f"/App/{params['featurename']}/{params['microservicename']}/"
            },
            {
                'Name': 'AccountID',
                'Value': '!Sub ${AWS::AccountId}'
            },
            {
                'Name': 's3bucket',
                'Value': '!Sub ${AWS::AccountId}-reports'
            },
            {
                'Name': 'queue',
                'Value': 'https://sqs.sa-east-1.amazonaws.com/049557819541/DevSecOps-ToolsReports'
            },
            {
                'Name': 'microservicename',
                'Value': params['microservicename']
            },
            {
                'Name': 'featurename',
                'Value': params['featurename']
            }
        ]
        title = 'Aqua'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Aqua-{params['branchname']}"
        aqua = self.create_codebuild(title, name.lower(), env, image, '/common/container-security/buildspec.yml')
        return aqua

    def PublishECRDev(self, **params):
        env =[
            {
                'Name' : 'pipeline_environment',
                'Value': params['branchname']

            },
            {
                'Name': 'ecr_account',
                'Value': '!Ref DevToolsAccount'
            },
            {
                'Name': 'microservice_name',
                'Value': params['microservicename']
            },
            {
                'Name': 'feature_name',
                'Value': params['featurename']
            }
        ]

        title = 'PublishECRDev'
        image = self.ImageCustom('PublishECR', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-PublishECR-{params['branchname']}"
        ecr = self.create_codebuild(title, name.lower(), env, image, '/common/Publish/buildspec-to-dev.yml')
        return ecr

    def DeployECSDev(self, **params):
        env = []
        title = 'DeployECSDev'
        image = self.ImageCustom('DeployECS', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-DeployECS-{params['branchname']}"
        deploy_ecs = self.create_codebuild(title, name.lower(), env, image, '/common/deploy/buildspec_ecs.yml')
        return deploy_ecs

    def PublishECRHomol(self, **params):
        env = []
        title = 'PublishECRHomol'
        image = self.ImageCustom('PublishECR', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-PublishECR-{params['branchname']}"
        ecr = self.create_codebuild(title, name.lower(), env, image, '/common/publish/buildspec_ecr.yml')
        return ecr

    def DeployECSHomol(self, **params):
        env = []
        title = 'DeployECSHomol'
        image = self.ImageCustom('DeployECS', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-DeployECS-{params['branchname']}"
        deploy_ecs = self.create_codebuild(title, name.lower(), env, image, '/common/deploy/buildspec_ecs.yml')
        return deploy_ecs

    def ParametersApp(self, **params):
        env =[
            {
                'Name': 'microservicename',
                'Value': params['microservicename']
            },
            {
                'Name': 'featurename',
                'Value': params['featurename']
            }
        ]

        title = 'ParametersApp'
        image = self.ImageCustom('ParametersApp', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-ParametersApp-{params['branchname']}"
        deploy_ecs = self.create_codebuild(title, name.lower(), env, image, '/common/EnvParameters/buildspec.yml')
        return deploy_ecs

    def AuditApp(self, **params):
        # Todo: PIPELINETYPE requerer uma variável com o nome APP
        env =[
            {
                'Name' : 'PIPELINETYPE',
                'Value': params['branchname']

            }
        ]

        title = 'AuditApp'
        image = self.ImageCustom('AuditApp', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-AuditApp-{params['branchname']}"
        deploy_ecs = self.create_codebuild(title, name.lower(), env, image, '/common/audit/buildspec.yml')
        return deploy_ecs
