from templates.codepipeline.pipeline import NewPipeline
from templates.pipeline_template import NewTemplate
from troposphere import Template
from tools.validates import change_yml_to_json
import pytest
import time
import json
import os
import sys
import shutil


class TestCodePipeline:
    @pytest.fixture
    def params(self):
        actions = {
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
                    'configuration': {'ProjectName': 'proj', 'PrimarySource': 'App', 'InputArtifacts': 'App', 'runorder': '1'},
                    'type': 'Build',
                    'role': 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'
                },
            'stage':
                {
                    'name': 'Compilador'
                },
            'pipeline':
                {
                    'name': 'PipelineEcs',
                    'role': 'arn:aws:iam::033921349789:role/RoleCodepipelineRole'
                },
            'templates': ['app-ecs']
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
            "TestUnit": {
                "all": "imagem_TestUnit"
            },
            "Fortify": {
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
            'payload_6.yml'
        ]
        return payload

    def gerando_cloudformation(self, resource):
        cf = Template()
        if isinstance(resource, dict):
            for res in resource.values():
                cf.add_resource(res)
        elif isinstance(resource, list):
            for res in resource:
                cf.add_resource(res)
        resource_json = json.loads(cf.to_json())
        return resource_json

    def load_template(self, name_template, env=False):
        template_json = open('tests/payload-ecs/templates.json')
        json_template = template_json.read()
        template_json.close()
        template = json.loads(json_template)

        if template['name'] == name_template:
            return template['details']['pipeline']
        elif name_template == 'structure':
            return template['details']['structure']
        elif name_template == 'depends':
            return template['details']['depends']

    def load_yml(self, filename):
        filename = f"tests/payload-ecs/{filename}"
        f_template = open(filename)
        yml_template = f_template.read()
        f_template.close()
        json_template = change_yml_to_json(yml_template)
        return json_template

    def test_deve_retornar_parametros_da_pipeline(self, params):
        for template in params['templates']:
            app_ecs = NewTemplate('codepipeline_role',
                                  'codebuild_role', 'DevSecOps_Role')
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

    def gettemplate(self, payload, env):
        make = self.load_yml(payload)
        stages = make['pipeline'][env]
        runtime = make['runtime']
        params = {}
        for param in make['Parameter']:
            params.update(param)
        dados = {
            'stages': stages,
            'runtime': runtime,
            'params': params
        }
        return dados

    def test_deve_retornar_codebuild_do_template_app_ecs_sem_buildCustomizado(self, params, imageCustom):
        for name_template in params['templates']:
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            dados = self.gettemplate('payload_1.yml', env)
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 10
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'Deployecsdev' in cf['Resources']
            assert 'Fortify' in cf['Resources']
            assert 'Publishecrdev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'Testunit' in cf['Resources']
            assert '../01/python/3.7/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python/3.7/testunit/buildspec.yml' in cf[
                'Resources']['Testunit']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_estrutura_pipeline(self, params, imageCustom):
        for name_template in params['templates']:
            estrutura = self.load_template('structure', 'develop')
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            stage = 'Deploydev'
            cf = app.check_stage_not_env(estrutura, stage, 'develop')
            assert cf == True
            stage = 'DeployHomol'
            cf = app.check_stage_not_env(estrutura, stage, 'master')
            assert cf == True

    def test_deve_retornar_codebuild_do_template_app_ecs_com_buildCustomizado(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            dados = self.gettemplate('payload_1.yml', env)
            dados['params']['BuildCustom'] = 'True'
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)

            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 10
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'Deployecsdev' in cf['Resources']
            assert 'Fortify' in cf['Resources']
            assert 'Publishecrdev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'Testunit' in cf['Resources']
            assert 'pipeline/buildspec_build.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert 'pipeline/buildspec_testunit.yml' in cf['Resources']['Testunit']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_codebuild_do_template_app_ecs_com_action_customizado(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            dados = self.gettemplate('payload_5.yml', env)
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')

            cf_pipeline = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            templ_pipeline = 0
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 11
            assert 'Aqua' in cf['Resources']
            assert 'Build' in cf['Resources']
            assert 'Deployecsdev' in cf['Resources']
            assert 'Fortify' in cf['Resources']
            assert 'Publishecrdev' in cf['Resources']
            assert 'Sonar' in cf['Resources']
            assert 'Testunit' in cf['Resources']
            assert '../01/python/3.7/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python/3.7/testunit/buildspec.yml' in cf[
                'Resources']['Testunit']['Properties']['Source']['BuildSpec']
            assert 'testmultant' in cf['Resources']

    def test_deve_retornar_codebuild_do_template_app_ecs_com_stage_customizado(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template,  env)
            dados = self.gettemplate('payload_6.yml', env)
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)
            resources = list(cf['Resources'].keys())
            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 13
            assert 'Aqua' in resources
            assert 'Build' in resources
            assert 'Deployecsdev' in resources
            assert 'Fortify' in resources
            assert 'Publishecrdev' in resources
            assert 'Sonar' in resources
            assert 'Testunit' in cf['Resources']
            assert '../01/python/3.7/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert '../01/python/3.7/testunit/buildspec.yml' in cf[
                'Resources']['Testunit']['Properties']['Source']['BuildSpec']
            assert 'seguranca2' in resources
            assert 'seguranca1' in resources
            assert 'seguranca2' in resources
            assert 'seguranca2' in cf['Resources']['seguranca2']['Properties']['Name']
            assert 'seguranca1' in cf['Resources']['seguranca1']['Properties']['Name']
            assert 'seguranca2' in cf['Resources']['seguranca2']['Properties']['Name']

    def test_deve_retornar_source_do_template_app_ecs_sem_source_customizado(self, params):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            template_yml = self.load_yml('payload_1.yml')
            stages = template_yml['pipeline'][env]
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(
                stages, env, reponame, 'codebuild_role', 'release-1.19')
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
            env = 'develop'
            name_template = pipe
            template_yml = self.load_yml('payload_3.yml')
            stages = template_yml['pipeline'][env]
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(
                stages, env, reponame, 'codebuild_role', 'release-1.19')
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
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            template_yml = self.load_yml('payload_4.yml')
            stages = template_yml['pipeline'][env]
            reponame = template_yml['Parameter'][0]['Projeto']
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            cf_pipeline = app.generate_sources(
                stages, 'develop', reponame, 'codebuild_role', 'release-1.19')
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

    def generate_action(self, name_template, env, payload, imageCustom):
        template_pipeline = self.load_template(name_template, env)
        dados = self.gettemplate(payload, env)
        reponame = dados['params']['Projeto']
        app = NewTemplate('codepipeline_role',
                          'codebuild_role', 'DevSecOps_Role')
        cf_codebuild = app.generate_codebuild(
            dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)

        cf_pipeline = app.generate_action(
            dados['stages'], template_pipeline, cf_codebuild, env)

        return cf_pipeline

    def test_deve_retornar_uma_lista_de_resources_que_pipeline_depende(self, params):
        env = 'develop'
        dep = self.load_template('depends')
        app = NewTemplate('codepipeline_role',
                          'codebuild_role', 'DevSecOps_Role')
        deps = app.create_depends('pipelineTeste', env, dep)
        cf = self.gerando_cloudformation(deps)
        assert 'SG' in cf['Resources'].keys()
        assert 'ECRpipelineTesteECRDevelop' in cf['Resources'].keys()

    def test_deve_retornar_action_do_template_app_ecs_validando_payloads(self, params, imageCustom, payloads):
        for pipe in params['templates']:
            for payload in payloads:
                cf_pipeline = self.generate_action(
                    pipe, 'develop', payload, imageCustom)
                cf = self.gerando_cloudformation(cf_pipeline)
                print(cf['Resources'].keys())
                print(payload)
                if payload == 'payload_5.yml' or payload == 'payload_8.yml':
                    assert len(cf['Resources']) == 11
                elif payload == 'payload_6.yml':
                    assert len(cf['Resources']) == 13
                else:
                    assert len(cf['Resources']) == 10

    def generate_pipeline(self, name_template, env, payload, imageCustom):
        template_pipeline = self.load_template(name_template, env)
        estrutura = self.load_template('structure', env)
        dados = self.gettemplate(payload, env)
        reponame = dados['params']['Projeto']
        app = NewTemplate('codepipeline_role',
                          'codebuild_role', 'DevSecOps_Role')
        resources = {}
        cf_codebuild = app.generate_codebuild(
            dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
        cf_source = app.generate_sources(
            dados['stages'], env, reponame, 'codebuild_role', 'release-1.19')
        cf_action = app.generate_action(
            dados['stages'], template_pipeline, cf_codebuild, env)

        resources.update(cf_source)
        resources.update(cf_action)
        cf_pipeline = app.generate_stage(
            template_pipeline, resources, env, estrutura)
        return cf_pipeline

    def test_deve_retornar_stage_do_template_app_ecs_payloads(self, params, imageCustom, payloads):
        for pipe in params['templates']:
            for payload in payloads:
                cf_pipeline = self.generate_pipeline(
                    pipe, 'develop', payload, imageCustom)
                cf = self.gerando_cloudformation(cf_pipeline)
                print(payload)
                print(cf['Resources'].keys())
                if payload == 'payload_6.yml':
                    assert len(cf['Resources']) == 5
                else:
                    assert len(cf['Resources']) == 3

    def test_deve_retornar_pipeline_verificando_stages_e_action(self, params, imageCustom, payloads):
        for name_template in params['templates']:
            for payload in payloads:
                env = 'develop'
                template_pipeline = self.load_template(name_template, env)
                estrutura = self.load_template('structure', env)
                dados = self.gettemplate(payload, env)
                reponame = dados['params']['Projeto']
                app = NewTemplate('codepipeline_role',
                                  'codebuild_role', 'DevSecOps_Role')
                resources = {}
                cf_codebuild = app.generate_codebuild(
                    dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
                cf_source = app.generate_sources(
                    dados['stages'], 'develop', reponame, 'codebuild_role', 'release-1.19')
                cf_action = app.generate_action(
                    dados['stages'], template_pipeline, cf_codebuild, env)

                resources.update(cf_source)
                resources.update(cf_action)
                cf_stages = app.generate_stage(
                    template_pipeline, resources, 'develop', estrutura)
                cf_pipeline = app.generate_pipeline(
                    cf_stages, f'{reponame}-develop')
                cf = self.gerando_cloudformation(cf_pipeline)
                if payload == 'payload_6.yml':
                    assert len(cf['Resources']['PipelinePythonDevelop']
                               ['Properties']['Stages']) == 5
                else:
                    assert len(cf['Resources']['PipelinePythonDevelop']
                               ['Properties']['Stages']) == 3

    def test_deve_salvar_pipeline_na_pasta_swap(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            estrutura = self.load_template('structure', env)
            dados = self.gettemplate('payload_6.yml', env)
            reponame = dados['params']['Projeto']
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            cf_source = app.generate_sources(
                dados['stages'], env, reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(
                dados['stages'], template_pipeline, cf_codebuild, env)

            resources.update(cf_source)
            resources.update(cf_action)
            cf_stages = app.generate_stage(
                template_pipeline, resources, env, estrutura)
            cf_pipeline = app.generate_pipeline(cf_stages, f"{reponame}-{env}")
            cf = self.gerando_cloudformation(cf_pipeline)
            template = json.dumps(cf)
            app.save_swap(reponame, template, env, '00000')
            assert os.path.isdir('swap') == True
            assert os.path.isfile(
                'swap/Pipeline-Python-develop-00000.json') == True
            os.remove('swap/Pipeline-Python-develop-00000.json')

    def test_deve_criar_pasta_swap(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, env)
            estrutura = self.load_template('structure', env)
            dados = self.gettemplate('payload_6.yml', env)
            reponame = dados['params']['Projeto']
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            resources = {}
            cf_codebuild = app.generate_codebuild(
                dados['runtime'], template_pipeline, dados['stages'], dados['params'], env, imageCustom)
            cf_source = app.generate_sources(
                dados['stages'], env, reponame, 'codebuild_role', 'release-1.19')
            cf_action = app.generate_action(
                dados['stages'], template_pipeline, cf_codebuild, env)

            resources.update(cf_source)
            resources.update(cf_action)
            cf_stages = app.generate_stage(
                template_pipeline, resources, env, estrutura)
            cf_pipeline = app.generate_pipeline(cf_stages, f"{reponame}-{env}")
            cf = self.gerando_cloudformation(cf_pipeline)
            template = json.dumps(cf)
            shutil.rmtree('swap')
            app.save_swap(reponame, template, env, '00000')
            assert os.path.isdir('swap') == True
            assert os.path.isfile(
                'swap/Pipeline-Python-develop-00000.json') == True
            os.remove('swap/Pipeline-Python-develop-00000.json')
            os.rmdir('swap')

    def test_deve_retornar_url_da_pipeline(self, params, imageCustom):
        for pipe in params['templates']:
            env = 'develop'
            name_template = pipe
            template_pipeline = self.load_template(name_template, 'develop')
            estrutura = self.load_template('structure', env)
            depends = self.load_template('depends', env)
            dados = self.gettemplate('payload_6.yml', env)
            app = NewTemplate('codepipeline_role',
                              'codebuild_role', 'DevSecOps_Role')
            template_params = {
                'env': env,
                'runtime': dados['runtime'],
                'stages': dados['stages'],
                'account': '000000',
                'pipeline_stages': template_pipeline,
                'params': dados['params'],
                'release': 'release-10',
                'imageCustom': imageCustom,
                'structure': estrutura,
                'depends': depends
            }
            file_template = app.generate(tp=template_params)
            print(file_template)
            assert os.path.isdir('swap') == True
            assert os.path.isfile(
                'swap/Pipeline-Python-develop-000000.json') == True
            os.remove('swap/Pipeline-Python-develop-000000.json')

    def test_deve_verificar_a_estrutura_da_pipeline(self, params, imageCustom, payloads):
        for name_template in params['templates']:
            for payload in payloads:
                env = 'develop'
                template_pipeline = self.load_template(name_template, env)
                estrutura = self.load_template('structure', env)
                depends = self.load_template('depends', env)
                dados = self.gettemplate(payload, env)
                codepipeline_role = "arn:aws:iam::033921349789:role/RoleCodepipelineRole"
                codebuild_role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
                DevSecOps_Role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
                app = NewTemplate(codepipeline_role,
                                  codebuild_role, DevSecOps_Role)
                template_params = {
                    'env': env,
                    'runtime': dados['runtime'],
                    'stages': dados['stages'],
                    'account': '000000',
                    'pipeline_stages': template_pipeline,
                    'params': dados['params'],
                    'release': 'release-10',
                    'imageCustom': imageCustom,
                    'structure': estrutura,
                    'depends': depends
                }
                file_template = app.generate(tp=template_params)
                # Abrindo a pipeline criada
                ft = open(file_template)
                ftemplate = json.loads(ft.read())
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
                print(payload)
                if payload == 'payload_6.yml':
                    assert len(
                        ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']) == 5
                else:
                    assert len(
                        ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']) == 3

                actions = ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']
                if payload == 'payload_1.yml':
                    print(len(actions[2]['Actions']))
                    assert len(actions) == 3
                    assert len(actions[0]['Actions']) == 2
                    assert len(actions[1]['Actions']) == 8
                    assert len(actions[2]['Actions']) == 2
                elif payload == 'payload_2.yml':
                    print(len(actions[2]['Actions']))
                    assert len(actions) == 3
                    assert len(actions[0]['Actions']) == 2
                    assert len(actions[1]['Actions']) == 8
                    assert len(actions[2]['Actions']) == 2
                elif payload == 'payload_3.yml':
                    print(len(actions[2]['Actions']))
                    assert len(actions) == 3
                    assert len(actions[0]['Actions']) == 3
                    assert len(actions[1]['Actions']) == 8
                    assert len(actions[2]['Actions']) == 2
                elif payload == 'payload_4.yml':
                    print(len(actions[2]['Actions']))
                    assert len(actions) == 3
                    assert len(actions[0]['Actions']) == 3
                    assert len(actions[1]['Actions']) == 8
                    assert len(actions[2]['Actions']) == 2
                elif payload == 'payload_5.yml':
                    print(len(actions[2]['Actions']))
                    assert len(actions) == 3
                    assert len(actions[0]['Actions']) == 3
                    assert len(actions[1]['Actions']) == 9
                    assert len(actions[2]['Actions']) == 2
                elif payload == 'payload_6.yml':
                    print(actions[4])
                    assert len(actions) == 5
                    assert len(actions[0]['Actions']) == 2
                    assert len(actions[1]['Actions']) == 8
                    assert len(actions[2]['Actions']) == 2
                    assert len(actions[4]['Actions']) == 2
                os.remove('swap/Pipeline-Python-develop-000000.json')

    def test_deve_retornar_pipeline_com_action_obrigatorio_com_source_personalizado(self, params, payloads, imageCustom):
        """
        Este teste deve validar a alteracao de um codebuild obrigatorio como o build, mas com o source personalizado
        """
        for name_template in params['templates']:
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            estrutura = self.load_template('structure', env)
            depends = self.load_template('depends', env)
            dados = self.gettemplate('payload_8.yml', env)
            codepipeline_role = "arn:aws:iam::033921349789:role/RoleCodepipelineRole"
            codebuild_role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            DevSecOps_Role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            app = NewTemplate(codepipeline_role,
                              codebuild_role, DevSecOps_Role)
            template_params = {
                'env': env,
                'runtime': dados['runtime'],
                'stages': dados['stages'],
                'account': '000000',
                'pipeline_stages': template_pipeline,
                'params': dados['params'],
                'release': 'release-10',
                'imageCustom': imageCustom,
                'structure': estrutura,
                'depends': depends
            }
            file_template = app.generate(tp=template_params)
            # Abrindo a pipeline criada
            ft = open(file_template)
            ftemplate = json.loads(ft.read())
            ft.close()
            resources = ftemplate['Resources'].keys()
            l_actions = ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']
            for actions in l_actions:
                for action in actions['Actions']:
                    if action['ActionTypeId']['Category'] != 'Source':
                        print(action)
                        if action['Name'] == 'Build':
                            assert [{'Name': 'Normalizacao'}] == [
                                item for item in action['InputArtifacts'] if item['Name'] == 'Normalizacao']
                            assert 'Normalizacao' == action['Configuration']['PrimarySource']
                        if action['Name'] == 'Testunit':
                            assert [{'Name': 'Normalizacao'}] == [
                                item for item in action['InputArtifacts'] if item['Name'] == 'Normalizacao']
                            assert 'Normalizacao' == action['Configuration']['PrimarySource']
                        if action['Name'] == 'Sonar':
                            assert [{'Name': 'Normalizacao'}] == [
                                item for item in action['InputArtifacts'] if item['Name'] == 'Normalizacao']
                            assert 'Normalizacao' == action['Configuration']['PrimarySource']

    def test_deve_retornar_pipeline_com_action_customizado_com_multiplos_sources(self, params, payloads, imageCustom):
        """
        Este teste deve validar a alteracao de um codebuild obrigatorio como o build, mas com o source personalizado
        """
        for name_template in params['templates']:
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            estrutura = self.load_template('structure', env)
            depends = self.load_template('depends', env)
            dados = self.gettemplate('payload_8.yml', env)
            codepipeline_role = "arn:aws:iam::033921349789:role/RoleCodepipelineRole"
            codebuild_role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            DevSecOps_Role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            app = NewTemplate(codepipeline_role,
                              codebuild_role, DevSecOps_Role)
            template_params = {
                'env': env,
                'runtime': dados['runtime'],
                'stages': dados['stages'],
                'account': '000000',
                'pipeline_stages': template_pipeline,
                'params': dados['params'],
                'release': 'release-10',
                'imageCustom': imageCustom,
                'structure': estrutura,
                'depends': depends
            }
            file_template = app.generate(tp=template_params)
            # Abrindo a pipeline criada
            ft = open(file_template)
            ftemplate = json.loads(ft.read())
            ft.close()
            resources = ftemplate['Resources'].keys()
            l_actions = ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']
            for actions in l_actions:
                for action in actions['Actions']:
                    if action['ActionTypeId']['Category'] != 'Source':
                        if action['Name'] == 'Normalizacao':
                            print(action)
                            assert [{'Name': 'App'}, {'Name': 'App2'}, {
                                'Name': 'App3'}] == action['InputArtifacts']
                            assert 'App' == action['Configuration']['PrimarySource']
                        if action['Name'] == 'Testmultant':
                            print(action)
                            assert [{'Name': 'Build'}
                                    ] == action['InputArtifacts']
                            assert 'Build' == action['Configuration']['PrimarySource']

    def test_deve_retornar_pipeline_com_stages_ordenados(self, params, payloads, imageCustom):
        """
        Este teste deve validar a alteracao de um codebuild obrigatorio como o build, mas com o source personalizado
        """
        for name_template in params['templates']:
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            estrutura = self.load_template('structure', env)
            depends = self.load_template('depends', env)
            dados = self.gettemplate('payload_9.yml', env)
            codepipeline_role = "arn:aws:iam::033921349789:role/RoleCodepipelineRole"
            codebuild_role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            DevSecOps_Role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
            app = NewTemplate(codepipeline_role,
                              codebuild_role, DevSecOps_Role)
            template_params = {
                'env': env,
                'runtime': dados['runtime'],
                'stages': dados['stages'],
                'account': '000000',
                'pipeline_stages': template_pipeline,
                'params': dados['params'],
                'release': 'release-10',
                'imageCustom': imageCustom,
                'structure': estrutura,
                'depends': depends
            }
            file_template = app.generate(tp=template_params)
            # Abrindo a pipeline criada
            ft = open(file_template)
            ftemplate = json.loads(ft.read())
            ft.close()
            resources = ftemplate['Resources'].keys()
            l_actions = ftemplate['Resources']['PipelinePythonDevelop']['Properties']['Stages']

            list_stages = [stage['Name'] for stage in l_actions]
            print(list_stages)
            assert ['Source', 'Continuous_Integration', 'Seguranca',
                    'Seguranca3', 'DeployDev'] == list_stages

    def test_deve_retornar_codebuild_eh_madatorio(self, params):
        for name_template in params['templates']:
            buildName = ['Build', 'Customizado']
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            pipeline = NewTemplate('codepipeline_role',
                                   'codebuild_role', 'DevSecOps_Role')
            mandatorio = pipeline.codebuild_mandatory(
                buildName[0], template_pipeline)
            customizado = pipeline.codebuild_mandatory(
                buildName[1], template_pipeline)
            assert mandatorio == True
            assert customizado == False

    def test_deve_retornar_codebuild_com_source_personalizado(self, params):
        for name_template in params['templates']:
            env = 'develop'
            template_pipeline = self.load_template(name_template, env)
            pipeline = NewTemplate('codepipeline_role',
                                   'codebuild_role', 'DevSecOps_Role')
            source1 = pipeline.check_is_not_codebuild(
                'Source', template_pipeline)
            source2 = pipeline.check_is_not_codebuild(
                'Build', template_pipeline)
            source3 = pipeline.check_is_not_codebuild(
                'Agendamento1', template_pipeline)
            source4 = pipeline.check_is_not_codebuild(
                'AprovacaoPO', template_pipeline)

            assert source1 == True
            assert source2 == False
            assert source3 == True
            assert source4 == True

    def test_deve_retornar_pipeline_master(self, params, imageCustom, payloads):
        for pipe in params['templates']:
            cf_pipeline = self.generate_pipeline(
                pipe, 'master', 'payload_1.yml', imageCustom)
            cf = self.gerando_cloudformation(cf_pipeline)
            print(cf['Resources'].keys())
            assert len(cf['Resources']) == 7

    def create_pipeline(self, name_template, env, imageCustom):
        template_pipeline = self.load_template(name_template, env)
        estrutura = self.load_template('structure', env)
        depends = self.load_template('depends', env)
        dados = self.gettemplate('payload_11.yml', env)
        codepipeline_role = "arn:aws:iam::033921349789:role/RoleCodepipelineRole"
        codebuild_role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
        DevSecOps_Role = "arn:aws:iam::033921349789:role/RoleCodeBuildRole"
        app = NewTemplate(codepipeline_role,
                          codebuild_role, DevSecOps_Role)
        template_params = {
            'env': env,
            'runtime': dados['runtime'],
            'stages': dados['stages'],
            'account': '000000',
            'pipeline_stages': template_pipeline,
            'params': dados['params'],
            'release': 'release-10',
            'imageCustom': imageCustom,
            'structure': estrutura,
            'depends': depends
        }
        file_template = app.generate(tp=template_params)

        # Abrindo a pipeline criada
        ft = open(file_template)
        ftemplate = json.loads(ft.read())
        ft.close()
        return ftemplate

    def test_deve_retornar_pipeline_com_action_de_aprovacao(self, params, payloads, imageCustom):
        """
        Este teste deve validar a alteracao de um codebuild obrigatorio como o build, mas com o source personalizado
        """
        for name_template in params['templates']:
            env = 'master'
            ftemplate = self.create_pipeline(
                name_template, env, imageCustom)
            env_ = env.capitalize()
            pipe_name = f'PipelinePython{env_}'
            l_actions = ftemplate['Resources']['PipelinePythonMaster']['Properties']['Stages']
            cont = 0
            for actions in l_actions:
                for action in actions['Actions']:
                    if action['ActionTypeId']['Category'] == 'Approval':
                        cont += 1

            assert cont == 2

    def test_deve_verificar_se_action_nao_estao_vazios(self, params, payloads, imageCustom):
        """
        Este teste deve validar a alteracao de um codebuild obrigatorio como o build, mas com o source personalizado
        """
        for name_template in params['templates']:
            for env in ['develop', 'master']:
                ftemplate = self.create_pipeline(
                    name_template, env, imageCustom)
                env_ = env.capitalize()
                pipe_name = f'PipelinePython{env_}'
                l_actions = ftemplate['Resources'][pipe_name]['Properties']['Stages']
                cont = 0
                for actions in l_actions:
                    assert len(actions['Actions']) != 0

    def test_deve_verificar_se_foi_removido_o_campo_type(self, params, payloads, imageCustom):
        """
        Esse teste tem que validar se o campo type inserido no template foi removido.

        type é utilizado para informar o tipo do action
        """
        for name_template in params['templates']:
            for env in ['develop', 'master']:
                ftemplate = self.create_pipeline(
                    name_template, env, imageCustom)
                env_ = env.capitalize()
                pipe_name = f'PipelinePython{env_}'
                l_actions = ftemplate['Resources'][pipe_name]['Properties']['Stages']
                cont = 0
                type_codebuild = False
                for actions in l_actions:
                    for confs in actions['Actions']:
                        assert 'type' not in confs['Configuration']

    def test_deve_verificar_se_foi_removido_o_campo_runorder_do_config(self, params, payloads, imageCustom):
        """
        Esse teste tem que validar se o campo runorder inserido no template foi removido.

        """
        for name_template in params['templates']:
            for env in ['develop', 'master']:
                ftemplate = self.create_pipeline(
                    name_template, env, imageCustom)
                env_ = env.capitalize()
                pipe_name = f'PipelinePython{env_}'

                l_actions = ftemplate['Resources'][pipe_name]['Properties']['Stages']
                cont = 0
                runorder = False
                for actions in l_actions:
                    for confs in actions['Actions']:
                        assert 'runorder' not in confs['Configuration']

    def test_deve_validar_os_stages_customizados_action_InvokeLambda_Custom_Approval(self, params, payloads, imageCustom):
        """
        Esse teste tem que validar se o campo runorder inserido no template foi removido.

        """
        for name_template in params['templates']:
            for env in ['develop']:
                ftemplate = self.create_pipeline(
                    name_template, env, imageCustom)
                env_ = env.capitalize()
                pipe_name = f'PipelinePython{env_}'

                l_stages = ftemplate['Resources'][pipe_name]['Properties']
                for stages in l_stages['Stages']:
                    print(stages['Name'])
                    if 'source' == stages['Name'].lower():
                        assert len(stages['Actions']) == 2
                        assert 'sharedlibrary' == stages['Actions'][0]['Name'].lower(
                        )
                        assert 'pipeline-python' == stages['Actions'][1]['Name'].lower()

                    elif 'continuous_integration' == stages['Name'].lower():
                        assert len(stages['Actions']) == 11
                        assert 'controlversion' == stages['Actions'][0]['Name'].lower(
                        )
                        assert 'sonar' == stages['Actions'][2]['Name'].lower()
                        assert 'testunit' == stages['Actions'][3]['Name'].lower(
                        )
                        assert 'build' == stages['Actions'][4]['Name'].lower()
                        assert 'aqua' == stages['Actions'][5]['Name'].lower(
                        )
                        assert 'auditapp' == stages['Actions'][6]['Name'].lower(
                        )
                        assert 'parametersapp' == stages['Actions'][7]['Name'].lower(
                        )
                        assert 'normalizacao' == stages['Actions'][8]['Name'].lower(
                        )
                        assert 'rodalambda' == stages['Actions'][9]['Name'].lower(
                        )
                        assert 'gonogo' == stages['Actions'][10]['Name'].lower(
                        )

                    elif 'deploydev' == stages['Name'].lower():
                        assert len(stages['Actions']) == 2
                        assert 'publishecrdev' == stages['Actions'][0]['Name'].lower(
                        )
                        assert 'deployecsdev' == stages['Actions'][1]['Name'].lower(
                        )
