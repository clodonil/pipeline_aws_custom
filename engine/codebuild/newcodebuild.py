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
         sast = self.create_codebuild('SAST', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')                
         return sast

     def Sonar(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         sonar = self.create_codebuild('SONAR', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return sonar

     def TestUnit(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         testunit = self.create_codebuild('TestUnit', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return testunit


     def Build(self, runtime):
         env = {"Name" : "Var1","Value": 'Var2'}
         build = self.create_codebuild('Build', env, 'linuxdockerhub',f'/{runtime}/build/buildspec.yml')
         return build

     def Deploy_ECS(self, env):
         code = []
         if env == 'dev':
            env = {"Name" : "Var1","Value": 'Var2'}
            code.append(self.create_codebuild('DeployECS', env, False,'/common/deploy/buildspec_ecs.yml'))
         elif env == 'prod':   
             code.append(self.create_codebuild('DeployECS', env, False,'/common/deploy/buildspec_ecs.yml'))
             code.append(self.create_codebuild('DeployECS', env, False,'/common/deploy/buildspec_ecs.yml'))
         return code

     def Deploy_EKS(self, env):
         env = {"Name" : "Var1","Value": 'Var2'}
         code = []
         if env == 'dev':
            code.append(self.create_codebuild('DeployEKS',  env, False,'/common/deploy/buildspec_eks.yml'))
         elif env == 'prod':   
            code.append(self.create_codebuild('DeployEKS',  env, False,'/common/deploy/buildspec_eks.yml'))
            code.append(self.create_codebuild('DeployEKS', env, False,'/common/deploy/buildspec_eks.yml'))
         return code

     def Deploy_Lambda(self):
         env = {"Name" : "Var1","Value": 'Var2'}
         lambdas = self.create_codebuild('DeployLambda', env, False,'common/deploy/buildspec_lambda.yml')
         return lambdas

     def Publish_ECR(self):
         env = {"Name" : "Var1","Value": 'Var2'}
         ecr = self.create_codebuild('PublishECR', env, False,'/common/publish/buildspec_ecr.yml')                
         return [ecr]

     def Publish_S3(self):
         env = {"Name" : "Var1","Value": 'Var2'}
         s3 = self.create_codebuild('PublishS3', env, False,'/common/publish/buildspec_s3.yml')
         return s3

     def Security(self):
         env = {"Name" : "Var1","Value": 'Var2'}
         aqua = self.create_codebuild('Aqua', env, 'imagem_do_docker_aqua','/common/aqua/buildspec.yml')
         return [aqua]

     def new_app_ecs(self, name, runtime, env):
        if name == 'ci':
           sast = self.Sast(runtime)
           sonar = self.Sonar(runtime)
           testunit = self.TestUnit(runtime)
           build = self.Build(runtime)
           return [ sast, sonar, testunit, build ]

        elif name == 'security':
            return self.Security()

        elif name == 'publish':
            return self.Publish_ECR()

        elif name == 'deploy':
            return self.Deploy_ECS(env)
        return []    

