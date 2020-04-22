from templates.codepipeline.pipeline import NewPipeline
from templates.pipeline_template import NewTemplate
from troposphere import Template
from tools.validates import change_yml_to_json
import pytest
import json
import os


class TestCodePipeline:
    @pytest.fixture
    def params(self):
        actions= {
            'source':
                {
                    'name': 'source',
                    'runorder': 1,
                    'configuration':  {'BranchName': 'release', 'RepositoryName': 'sharedlibrary'},
                    'type': 'Source',
                    'role': 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'
                },
            'action':
                {
                    'name': 'compilar',
                    'runorder': 1,
                    'configuration': {'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': 'App', 'runorder': '1'},
                    'type': 'Build',
                    'role': 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'
                },
            'stage':
                {
                    'name' : 'Compilador'
                },
            'pipeline':
                {
                    'name' : 'PipelineEcs',
                    'role': 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'
                },
            'templates':['app-ecs']
        }
        return actions

    @pytest.fixture
    def imageCustom(self):
        imgcustom = {
            "Aqua": {
                "all": "imagem_Aqua"
            },
            "Build": {
                "all": "image_Build",
                "python37": "image_custom"
            },
            "BuildTestUnit": {
                "all": "imagem_TestUnit"
            },
            "SAST": {
                "all": "imagem_sast"
            },
            "Sonar": {
                "all": "imagem_sonar"
            }
        }
        return imgcustom

    @pytest.fixture
    def payloads(self):
        payload = [
            'payload_1.yml',
            'payload_2.yml',
            'payload_3.yml',
            'payload_4.yml',
            'payload_5.yml',
            'payload_6.yml',
        ]
        return payload
    def gerando_cloudformation(self, resource):
        cf = Template()
        if isinstance(resource, dict):
            for res in resource.values():
                cf.add_resource(res)
        else:
            cf.add_resource(resource)
        resource_json = json.loads(cf.to_json())
        return resource_json

    def load_template(self, name_template, env):
        template_json = open('tests/payload/templates.json')
        json_template = template_json.read()
        template_json.close()
        template = json.loads(json_template)

        if template['name'] == name_template:
            print(template['name'])
            return template['details'][env]

    def load_yml(self, filename):
        filename = f"tests/payload/{filename}"
        f_template = open(filename)
        yml_template = f_template.read()
        f_template.close()
        json_template = change_yml_to_json(yml_template)
        return json_template

    def test_deve_retornar_parametros_da_pipeline(self, params):
        for template in params['templates']:
            app_ecs = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app_ecs.pipeline_parameter()
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf)
            assert len(cf['Resources']) == 10
            assert cf['Resources']['PrivateSubnetOne']['Default'] == '/Networking/PrivateSubnetOne'
            assert cf['Resources']['PrivateSubnetTwo']['Default'] == '/Networking/PrivateSubnetTwo'
            assert cf['Resources']['VPCID']['Default'] == '/Networking/VPCID'
            assert cf['Resources']['DevAccount']['Default'] == '/Accounts/Dev'
            assert cf['Resources']['HomologAccount']['Default'] == '/Accounts/Homolog'
            assert cf['Resources']['ProdAccount']['Default'] == '/Accounts/Prod'
            assert cf['Resources']['KMSKeyArn']['Default'] == '/Shared/KMSKeyArn'
            assert cf['Resources']['TokenAqua']['Default'] == '/Shared/TokenAqua'
            assert cf['Resources']['DevSecOpsAccount']['Default'] == '/Accounts/DevSecOps'
            assert cf['Resources']['DevToolsAccount']['Default'] == '/Accounts/DevTools'

    def test_deve_retornar_codebuild_do_template_app_ecs_sem_buildCustomizado(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            make = self.load_yml('payload_1.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(runtime, template_pipeline, stages, params, env, imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 7
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'DeployECSDev' in cf['Resources']
            assert 'SAST' in cf['Resources']
            assert 'PublishECRDev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'BuildTestUnit' in cf['Resources']
            assert '../01/python37/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python37/testunit/buildspec.yml' in cf['Resources']['BuildTestUnit']['Properties']['Source']['BuildSpec']


    def test_deve_retornar_codebuild_do_template_app_ecs_com_buildCustomizado(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            make = self.load_yml('payload_1.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            params['BuildCustom'] = 'True'
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(runtime, template_pipeline, stages, params, env, imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 7
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'DeployECSDev' in cf['Resources']
            assert 'SAST' in cf['Resources']
            assert 'PublishECRDev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'BuildTestUnit' in cf['Resources']
            assert 'pipeline/buildspec_build.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert 'pipeline/buildspec_testunit.yml' in cf['Resources']['BuildTestUnit']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_codebuild_do_template_app_ecs_com_action_customizado(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_5.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            templ_pipeline = 0
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 8
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'DeployECSDev' in cf['Resources']
            assert 'SAST' in cf['Resources']
            assert 'PublishECRDev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'BuildTestUnit' in cf['Resources']
            assert '../01/python37/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python37/testunit/buildspec.yml' in cf['Resources']['BuildTestUnit']['Properties']['Source']['BuildSpec']
            assert 'testmultant' in cf['Resources']


    def test_deve_retornar_codebuild_do_template_app_ecs_com_stage_customizado(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)
            resources = list(cf['Resources'].keys())
            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 10
            assert 'Aqua' in resources
            assert 'Build' in resources
            assert 'DeployECSDev' in resources
            assert 'SAST' in resources
            assert 'PublishECRDev' in resources
            assert 'Sonar' in resources
            assert 'BuildTestUnit' in cf['Resources']
            assert '../01/python37/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python37/testunit/buildspec.yml' in cf['Resources']['BuildTestUnit']['Properties']['Source']['BuildSpec']
            assert 'seguranca2' in resources
            assert 'seguranca1' in resources
            assert 'seguranca2' in resources
            assert 'seguranca2' in cf['Resources']['seguranca2']['Properties']['Name']
            assert 'seguranca1' in cf['Resources']['seguranca1']['Properties']['Name']
            assert 'seguranca2' in cf['Resources']['seguranca2']['Properties']['Name']

    def test_deve_retornar_source_do_template_app_ecs_sem_source_customizado(self, params):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            template_yml = self.load_yml('payload_1.yml')
            stages = template_yml['pipeline']
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 2
            assert 'SharedLibrary' in cf['Resources']
            assert 'release-1.19' == cf['Resources']['SharedLibrary']['Configuration']['BranchName']
            assert 'false' == cf['Resources']['SharedLibrary']['Configuration']['PollForSourceChanges']
            assert 'pipelineaws-sharedlibrary' == cf['Resources']['SharedLibrary']['Configuration']['RepositoryName']
            assert 'PipelinePython' in cf['Resources']
            assert 'develop' == cf['Resources']['PipelinePython']['Configuration']['BranchName']
            assert 'Pipeline-Python' == cf['Resources']['PipelinePython']['Configuration']['RepositoryName']

    def test_deve_retornar_source_do_template_app_ecs_com_source_customizado_sem_branch(self, params):
        for pipe in params['templates']:
            name_template = pipe
            template_yml = self.load_yml('payload_3.yml')
            stages = template_yml['pipeline']
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 3
            assert 'SharedLibrary' in cf['Resources']
            assert 'release-1.19' == cf['Resources']['SharedLibrary']['Configuration']['BranchName']
            assert 'false' == cf['Resources']['SharedLibrary']['Configuration']['PollForSourceChanges']
            assert 'pipelineaws-sharedlibrary' == cf['Resources']['SharedLibrary']['Configuration']['RepositoryName']
            assert 'PipelinePython' in cf['Resources']
            assert 'develop' == cf['Resources']['PipelinePython']['Configuration']['BranchName']
            assert 'Pipeline-Python' == cf['Resources']['PipelinePython']['Configuration']['RepositoryName']
            assert 'Tools' in cf['Resources']
            assert 'develop' == cf['Resources']['Tools']['Configuration']['BranchName']
            assert 'Tools' == cf['Resources']['Tools']['Configuration']['RepositoryName']

    def test_deve_retornar_source_do_template_app_ecs_com_source_customizado_com_branch(self, params):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            template_yml = self.load_yml('payload_4.yml')
            stages = template_yml['pipeline']
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources']['Tools'])
            assert len(cf['Resources']) == 3
            assert 'SharedLibrary' in cf['Resources']
            assert 'release-1.19' == cf['Resources']['SharedLibrary']['Configuration']['BranchName']
            assert 'false' == cf['Resources']['SharedLibrary']['Configuration']['PollForSourceChanges']
            assert 'pipelineaws-sharedlibrary' == cf['Resources']['SharedLibrary']['Configuration']['RepositoryName']
            assert 'SharedLibrary' in cf['Resources']
            assert 'develop' == cf['Resources']['PipelinePython']['Configuration']['BranchName']
            assert 'Pipeline-Python' == cf['Resources']['PipelinePython']['Configuration']['RepositoryName']
            assert 'Tools' in cf['Resources']
            assert 'master' == cf['Resources']['Tools']['Configuration']['BranchName']
            assert 'Tools' == cf['Resources']['Tools']['Configuration']['RepositoryName']

    def test_deve_retornar_action_do_template_app_ecs_payload_1(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_1.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 7

    def test_deve_retornar_action_do_template_app_ecs_payload_2(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_2.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 7

    def test_deve_retornar_action_do_template_app_ecs_payload_3(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template,'develop')
            make = self.load_yml('payload_3.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 7

    def test_deve_retornar_action_do_template_app_ecs_payload_4(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template,'develop')
            make = self.load_yml('payload_4.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 7

    def test_deve_retornar_action_do_template_app_ecs_payload_5(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template,'develop')
            make = self.load_yml('payload_5.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 8

    def test_deve_retornar_action_do_template_app_ecs_payload_6(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template,'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_pipeline = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 10

    def test_deve_retornar_stage_do_template_app_ecs_payload_1(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_1.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 5

    def test_deve_retornar_stage_do_template_app_ecs_payload_2(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template,'develop')
            make = self.load_yml('payload_2.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 5

    def test_deve_retornar_stage_do_template_app_ecs_payload_3(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_3.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 5

    def test_deve_retornar_stage_do_template_app_ecs_payload_4(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_4.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')

            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'])
            assert len(cf['Resources']) == 5

    def test_deve_retornar_stage_do_template_app_ecs_payload_5(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_5.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 5

    def test_deve_retornar_stage_do_template_app_ecs_payload_6(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_pipeline = app.generate_stage(template_pipeline, resources, 'develop')
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'])
            assert len(cf['Resources']) == 7

    def test_deve_retornar_pipeline(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, reponame, 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_stages = app.generate_stage(template_pipeline, resources, 'develop')
            cf_pipeline = app.generate_pipeline(cf_stages, f'{reponame}-develop')
            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'])
            len(cf['Resources']['PipelinePythonDevelop']['Properties']['Stages']) == 7

    def test_deve_salvar_pipeline_na_pasta_swap(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', params['Projeto'], 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, params['Projeto'], 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_stages = app.generate_stage(template_pipeline, resources, 'develop')
            cf_pipeline = app.generate_pipeline(cf_stages, f"{reponame}-develop")
            cf = self.gerando_cloudformation(cf_pipeline)
            template = json.dumps(cf)
            app.save_swap(reponame, template, 'develop', '00000')
            assert os.path.isdir('swap') == True
            assert os.path.isfile('swap/Pipeline-Python-develop-00000.json') == True
            os.remove('swap/Pipeline-Python-develop-00000.json')

    def test_deve_criar_pasta_swap(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            runtime = make['runtime']
            params = {}
            for param in make['Parameter']:
                params.update(param)
            reponame = params['Projeto']
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(runtime, template_pipeline, stages, params, 'develop', imageCustom)
            cf_source = app.generate_sources(stages, 'develop', params['Projeto'], 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(cf_codebuild, template_pipeline, params['Projeto'], 'develop')
            resources.update(cf_source)
            resources.update(cf_action)
            cf_stages = app.generate_stage(template_pipeline, resources, 'develop')
            cf_pipeline = app.generate_pipeline(cf_stages, f"{reponame}-develop")
            cf = self.gerando_cloudformation(cf_pipeline)
            template = json.dumps(cf)
            os.rmdir('swap')
            app.save_swap(reponame, template, 'develop', '00000')
            assert os.path.isdir('swap') == True
            assert os.path.isfile('swap/Pipeline-Python-develop-00000.json') == True
            os.remove('swap/Pipeline-Python-develop-00000.json')
            os.rmdir('swap')


    def test_deve_retornar_url_da_pipeline(self, params, imageCustom):
        for pipe in params['templates']:
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            make = self.load_yml('payload_6.yml')
            stages = make['pipeline']
            params = {}
            for param in make['Parameter']:
                params.update(param)

            env = 'develop'
            app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
            template_params = {
                'env': 'develop',
                'runtime': make['runtime'],
                'stages': make['pipeline'],
                'account': '000000',
                'pipeline_stages': template_pipeline,
                'params': params,
                'release': 'release-10',
                'imageCustom': imageCustom
            }
            file_template = app.generate(tp=template_params)
            print(file_template)
            assert os.path.isdir('swap') == True
            assert os.path.isfile('swap/Pipeline-Python-develop-000000.json') == True
            os.remove('swap/Pipeline-Python-develop-000000.json')

    def test_deve_retornar_securitygroup(self):
        app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
        sg = app.create_security_groups('Pipeline-Python', 'develop')
        cf = self.gerando_cloudformation(sg)
        print(cf)
        assert "SG" in cf["Resources"]
        assert "0.0.0.0/0" == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["CidrIp"]
        assert 0 == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["FromPort"]
        assert "TCP" == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["IpProtocol"]
        assert 65535 == cf["Resources"]["SG"]["Properties"]["SecurityGroupIngress"][0]["ToPort"]

    def test_deve_verificar_a_estrutura_da_pipeline(self, params, imageCustom, payloads):
        for pipe in params['templates']:
            for payload in payloads:
                name_template = pipe
                template_pipeline = self.load_template(name_template, 'develop')
                make = self.load_yml(payload)
                stages = make['pipeline']
                params = {}
                for param in make['Parameter']:
                    params.update(param)
                app = NewTemplate('codepipeline_role', 'codebuild_role', 'DevSecOps_Role')
                template_params = {
                    'env': 'develop',
                    'runtime': make['runtime'],
                    'stages': make['pipeline'],
                    'account': '000000',
                    'pipeline_stages': template_pipeline,
                    'params': params,
                    'release': 'release-10',
                    'imageCustom': imageCustom
                }
                file_template = app.generate(tp=template_params)
                ft = open(file_template)
                ftemplate= json.loads(ft.read())
                ft.close()
                resources = ftemplate['Resources'].keys()
                codebuilds = []
                sg = []
                for resource in resources:
                    if ftemplate['Resources'][resource]['Type'] == 'AWS::CodeBuild::Project':
                       name = ftemplate['Resources'][resource]['Properties']['Name']
                       codebuilds.append(name)
                    elif ftemplate['Resources'][resource]['Type'] == 'AWS::EC2::SecurityGroup':
                       sg.append(ftemplate['Resources'][resource])

                for resource in resources:
                    if ftemplate['Resources'][resource]['Type'] == 'AWS::CodePipeline::Pipeline':
                       for stages in (ftemplate['Resources'][resource]['Properties']['Stages']):
                           for action in stages['Actions']:
                              if action['ActionTypeId']['Category'] == 'Build':
                                 assert action['Configuration']['ProjectName'] in codebuilds
                assert sg
                os.remove('swap/Pipeline-Python-develop-000000.json')
