import os

# Filas SQS
filas = {
    "payload": "wasabi-payload",
    "processing" : "wasabi-processing",
    "deploy" : "wasabi-deploy"
}
polling_time = 60

#Tabela do Dynamodb
dynamodb = {
    'template' : "wasabi-template-produced"
}

aws_region = 'us-east-1'
s3_bucket = 'wasabi-templates'

### CodeBuild
codebuild_timeoutInMinutes = 10
codebuild_image_default = "aws/codebuild/standard:2.0"
RoleCodeBuild = "RoleCodeBuildRole"

### Codepipeline
RoleCodePipeline = "RoleCodepipelineRole"

DevSecOps_Role = "arn:aws:iam::000000000:role/DevOpsRole"

### SSM

VPCID = '/Networking/VPCID'
PrivateSubnetOne = '/Networking/PrivateSubnetOne'
PrivateSubnetTwo = '/Networking/PrivateSubnetTwo'
DevAccount = '/Accounts/Dev'
HomologAccount = '/Accounts/Homolog'
ProdAccount = '/Accounts/Prod'
KMSKeyArn = '/Shared/KMSKeyArn'
TokenAqua = '/Shared/TokenAqua'
DevSecOpsAccount = '/Accounts/DevSecOps'
DevToolsAccount = '/Accounts/DevTools'
