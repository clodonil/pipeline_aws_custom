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
codebuild_image_default = 'aws/codebuild/standard:2.0'
codebuild_role = 'arn:aws:iam::033921349789:role/RoleCodeBuildRole'
#vpc = os.environ['VPCID']
#subnet1 = os.environ['SUBNET_A'
#subnet2 = os.environ['SUBNET_B'
#securitygroup = os.environ['SECGROUP']

### Codepipeline
codepipeline_roles = 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'