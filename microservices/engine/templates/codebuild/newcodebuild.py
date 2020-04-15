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

    def project_name(self, name):
        p_name = []
        #name =  f'Codebuild-{name}'
        for letra in name.split('-'):
            p_name.append(letra.capitalize())
        name = '-'.join(p_name)
        project_name = ''.join(e for e in name if e.isalnum())
        return project_name

    def create_codebuild(self, name, envs, imagecustom=False, buildspec=False,):
        project_name = self.project_name(name)
        # imagem do codebuild
        if imagecustom:
            dockerimage = imagecustom
        else:
            dockerimage = self.image

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
            ImagePullCredentialsType = 'SERVICE_ROLE'
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

    def ControlVersion(self, **params):
        env = [
            {
                "Name" : 'Runtime',
                "Value" : params['runtime']
            }
        ]
        name = f"{params['featurename']}-{params['microservicename']}-ControlVersion-{params['branchname']}"
        controlversion = self.create_codebuild(
            name,
            env,
            False,
            f'common/controlversion/buildspec.yml'
        )

        return controlversion

    def BuildSAST(self, **params):
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

        name = f"{params['featurename']}-{params['microservicename']}-BuildSAST-{params['branchname']}"
        sast = self.create_codebuild(
            name,
            env,
            '984688426935.dkr.ecr.sa-east-1.amazonaws.com/appsec:latest',
            f"../01/{params['runtime']}/sast/buildspec.yml"
        )

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
        name = f"{params['featurename']}-{params['microservicename']}-Sonar-{params['branchname']}"
        sonar = self.create_codebuild(
            name,
            env,
            '049557819541.dkr.ecr.sa-east-1.amazonaws.com/codebuild-sonar:latest',
            f"../01/{params['runtime']}/sonarqube/buildspec.yml"
        )
        return sonar


    def BuildTestUnit(self, **params):
        env = []
        if params['custom']:
            buildspec = "pipeline/buildspec_testunit.yml"
        else:
            buildspec = f"../01/{params['runtime']}/testunit/buildspec.yml"

        name = f"{params['featurename']}-{params['microservicename']}-BuildTestUnit-{params['branchname']}"
        testunit = self.create_codebuild(
            name,
            env,
            False,
            buildspec
        )
        return testunit

    def Build(self, **params):
        env = []
        if params['custom']:
            buildspec = "pipeline/buildspec_build.yml"
        else:
            buildspec = f"../01/{params['runtime']}/build/buildspec.yml"

        name = f"{params['featurename']}-{params['microservicename']}-Build-{params['branchname']}"
        build = self.create_codebuild(
            name,
            env,
            False,
            buildspec
        )
        return build


    def Aqua(self, **params):
        env = []
        name = f"{params['featurename']}-{params['microservicename']}-Aqua-{params['branchname']}"
        aqua = self.create_codebuild(
            name,
            env,
            False,
            '/common/aqua/buildspec.yml'
        )
        return aqua

    def PublishECR(self, **params):
        env = []
        name = f"{params['featurename']}-{params['microservicename']}-PublishECR-{params['branchname']}"
        ecr = self.create_codebuild(
            name,
            env,
            False,
            '/common/publish/buildspec_ecr.yml'
        )
        return ecr

    def DeployECS(self, **params):
        env = []
        name = f"{params['featurename']}-{params['microservicename']}-DeployECS-{params['branchname']}"
        deploy_ecs = self.create_codebuild(
            name,
            env,
            False,
            '/common/deploy/buildspec_ecs.yml'
        )
        return deploy_ecs
