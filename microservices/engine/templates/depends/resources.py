from troposphere import Ref, Sub, ec2
from troposphere.ecr import Repository
from tools.log import logger
from awacs.aws import Allow, PolicyDocument, AWSPrincipal, Statement
from awacs.aws import Action
from awacs.aws import Principal
from awacs.iam import ARN as IAM_ARN


class DepResource:
    def SG(self, name):
        project_name = f'SG'
        logger.info(f"Criando o Security Group: {project_name}")
        project_name = ''.join(e for e in project_name if e.isalnum())
        out_all_rule = ec2.SecurityGroupRule(
            IpProtocol='TCP', FromPort=0, ToPort=65535, CidrIp='0.0.0.0/0'
        )
        sg = ec2.SecurityGroup(
            project_name,
            VpcId=Ref("VPCID"),
            GroupName=name,
            GroupDescription='This security group is used to control access to the container',
            SecurityGroupIngress=[out_all_rule]
        )
        return [sg]

    def ECR(self, name):
        logger.info(f"Criando o ECR: {name}")
        project_name = f'ECR{name}'
        resource_name = ''.join(e for e in project_name if e.isalnum())
        p_service = Principal("Service", "codebuild.amazonaws.com")
        p_aws = Principal("AWS", [
            Sub("arn:aws:iam::${DevAccount}:root"),
            Sub("arn:aws:iam::${HomologAccount}:root"),
            Sub("arn:aws:iam::${ProdAccount}:root")
        ]
        )

        policydocument = PolicyDocument(
            Version='2008-10-17',
            Statement=[
                Statement(
                    Sid='AllowPushPull',
                    Effect=Allow,
                    Principal=p_service,
                    Action=[Action("ecr", "*")],
                ),
                Statement(
                    Sid='AllowPushPull',
                    Effect=Allow,
                    Principal=p_aws,
                    Action=[Action("ecr", "*")],
                ),

            ]
        )
        resource_ecr = Repository(
            resource_name, RepositoryName=name.lower(), RepositoryPolicyText=policydocument)
        return [resource_ecr]

    def SGDevelop(self, name):
        return self.SG(name)

    def SGMaster(self, name):
        return self.SG(name)

    def ECRDevelop(self, name):
        return self.ECR(name)

    def ECRHomolog(self, name):
        return self.ECR(name)

    def ECRMaster(self, name):
        return self.ECR(name)

    def SNS(self, name):
        return []
