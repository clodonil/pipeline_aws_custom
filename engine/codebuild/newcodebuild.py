from troposphere.codebuild import Artifacts, Environment, Source, Project, VpcConfig
from troposphere import Template

class NewCodeBuild:
     def __init__(self, roleCodeBuild, kMSKeyArn, vpcid, privatesubnetOne, privatesubnetTwo, sgpipeline):
         self.roleCodeBuild = roleCodeBuild
         self.kMSKeyArn = kMSKeyArn
         self.vpcid = vpcid
         self.privatesubnetOne = privatesubnetOne
         self.privatesubnetTwo = privatesubnetTwo
         self.sgpipeline = sgpipeline
         self.computeType='BUILD_GENERAL1_SMALL'
         self.image='aws/codebuild/standard:2.0'
         self.type='LINUX_CONTAINER'
         self.artifacts = Artifacts(Type='CODEPIPELINE')
         self.vpcConfig = VpcConfig(VpcId = self.vpcid,Subnets = [self.privatesubnetOne,self.privatesubnetTwo], SecurityGroupIds = [self.sgpipeline])
         self.timeoutInMinutes = 10

     
     def create_codebuild(self, name, env, imagecustom=False, buildspec=False,):

         project_name = f'{name}'
         # imagem do codebuild
         if imagecustom:
            dockerimage= imagecustom
         else:
            dockerimage= self.image

         # Path do codebuild
         if buildspec:
            pathBuildSpec= buildspec
         else:                
            pathBuildSpec= f'pipeline/{name.lower()}_buildspec.yml'
       

         environment = Environment(
                                    ComputeType= self.computeType,
                                    Image= dockerimage,
                                    Type = self.type,
                                    EnvironmentVariables=[env],
                                    PrivilegedMode= 'true'
                                  )

         source = Source(            
                          BuildSpec= pathBuildSpec,
                          Type= 'CODEPIPELINE'
                        )

         codebuild = Project(
                              project_name,
                              Artifacts=self.artifacts,
                              Environment=environment,
                              Name=name,
                              ServiceRole=self.roleCodeBuild,
                              Source=source,
                              #EncryptionKey = self.kMSKeyArn,
                              TimeoutInMinutes = self.timeoutInMinutes,
                              VpcConfig = self.vpcConfig
                            )
         return codebuild

     def Sast(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         sast = self.create_codebuild('Sast', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')                
         return sast

     def Sonar(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         sonar = self.create_codebuild('Sonar', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return sonar

     def TestUnit(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         testunit = self.create_codebuild('TestUnit', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return testunit


     def Build(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         build = self.create_codebuild('Build', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return build

     def DeployECS(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         deploy_ecs = self.create_codebuild('DeployECS', env, False,'/common/deploy/buildspec_ecs.yml')
         return deploy_ecs

     def DeployEKS(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         deploy_eks = self.create_codebuild('DeployEKS', env, False,'/common/deploy/buildspec_eks.yml')
         return deploy_eks

     def DeployLambda(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         lambdas = self.create_codebuild('DeployLambda', env, False,'common/deploy/buildspec_lambda.yml')
         return lambdas

     def PublishECR(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         ecr = self.create_codebuild('PublishECR', env, False,'/common/publish/buildspec_ecr.yml')                
         return ecr

     def PublishS3(self):
         env = {"Name" : "Var1","Value": 'Var2'}
         s3 = self.create_codebuild('PublishS3', env, False,'/common/publish/buildspec_s3.yml')
         return s3

     def Aqua(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         aqua = self.create_codebuild('Aqua', env, 'imagem_do_docker_aqua','/common/aqua/buildspec.yml')
         return aqua
