from troposphere.codebuild import (
    Artifacts, Environment, Source, Project, VpcConfig)
from troposphere import Ref


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

    def create_codebuild(self, title, name, envs, imagecustom=False, buildspec=False,):
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
            pathBuildSpec = f'pipeline/{name.lower()}_buildspec.yml'

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
        env = [
            {
                "Name" : 'Runtime',
                "Value" : params['runtime']
            }
        ]
        title = 'ControlVersion'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-ControlVersion-{params['branchname']}"
        controlversion = self.create_codebuild('ControlVersion', name, env, image, f'common/controlversion/buildspec.yml')

        return controlversion

    def SAST(self, **params):
        env =[
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
        title = 'SAST'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-SAST-{params['branchname']}"
        sast = self.create_codebuild(title, name, env, image, f"../01/{params['runtime']}/sast/buildspec.yml")
        return sast

    def Sonar(self, **params):
        env = [
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
        sonar = self.create_codebuild(title, name, env, image, f"../01/{params['runtime']}/sonarqube/buildspec.yml")
        return sonar


    def BuildTestUnit(self, **params):
        env = []
        if params['custom']:
            buildspec = "pipeline/buildspec_testunit.yml"
        else:
            buildspec = f"../01/{params['runtime']}/testunit/buildspec.yml"

        title = 'BuildTestUnit'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-BuildTestUnit-{params['branchname']}"
        testunit = self.create_codebuild(title, name, env, image, buildspec)
        return testunit

    def Build(self, **params):
        env = []
        if params['custom']:
            buildspec = "pipeline/buildspec_build.yml"
        else:
            buildspec = f"../01/{params['runtime']}/build/buildspec.yml"

        title = 'Build'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Build-{params['branchname']}"
        build = self.create_codebuild(title, name, env, image, buildspec)
        return build


    def Aqua(self, **params):
        env = []
        title = 'Aqua'
        image = self.ImageCustom(title, params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-Aqua-{params['branchname']}"
        aqua = self.create_codebuild(title, name, env, image, '/common/aqua/buildspec.yml')
        return aqua

    def PublishECR(self, **params):
        env = []
        image = self.ImageCustom('PublishECR', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-PublishECR-{params['branchname']}"
        ecr = self.create_codebuild(f"PublishECR{params['branchname']}", name, env, image, '/common/publish/buildspec_ecr.yml')
        return ecr

    def DeployECS(self, **params):
        env = []
        image = self.ImageCustom('DeployECS', params['imageCustom'], params['runtime'])
        name = f"{params['featurename']}-{params['microservicename']}-DeployECS-{params['branchname']}"
        deploy_ecs = self.create_codebuild(f"DeployECS{params['branchname']}", name, env, image, '/common/deploy/buildspec_ecs.yml')
        return deploy_ecs
