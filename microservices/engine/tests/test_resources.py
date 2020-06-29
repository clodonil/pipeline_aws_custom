from troposphere import Template, Parameter, ec2, Ref
import pytest
from templates.depends.resources import DepResource
from templates.codepipeline.pipeline import NewPipeline
from templates.pipeline_template import NewTemplate
import json


class TestCodeBuild:

    def gerando_cloudformation(self, resource, parameters=None):
        template = Template()
        if parameters != None:
            for param in parameters:
                template.add_parameter(param)

        template.add_resource(resource)
        resource_json = json.loads(template.to_json())
        return resource_json

    def test_deve_retornar_um_repositorio_do_ecr(self):
        ecr_name = "projeto1teste"
        template = NewTemplate('codepipeline_role',
                               'codebuild_role', 'DevSecOps_Role')
        params = template.pipeline_parameter()
        proj = DepResource()
        ecr = proj.ECR(ecr_name)
        cftemplate = self.gerando_cloudformation(ecr, params)
        print(cftemplate)
        assert ecr_name == cftemplate['Resources']['ECRprojeto1teste']['Properties']['RepositoryName']

    def test_deve_retornar_securitygroup(self):
        resource = DepResource()
        sg = resource.SG('Pipeline-Python-develop')
        cf = self.gerando_cloudformation(sg)
        print(cf)
        assert "SG" in cf["Resources"]
        assert "0.0.0.0/0" == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["CidrIp"]
        assert 0 == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["FromPort"]
        assert "TCP" == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["IpProtocol"]
        assert 65535 == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["ToPort"]

    def test_deve_retornar_sns(self):
        resource = DepResource()
        sns = resource.SNS('teste')
        assert sns == []
