from templates.codebuild.newcodebuild import NewCodeBuild
from troposphere import Template
import pytest
import json


class TestCodeBuild:
    @pytest.fixture
    def params(self):
        msg = {
            'nome': 'TesteCodeBuild',
            'role': 'codebuild_role',
            'kms': 'kmskey',
            'env': [{'Name': 'varname1', 'Value':'varvalue1'}, {'Name': 'varname2', 'Value':'varvalue2'}],
            'runtime': ['python36']
         }
        return msg

    def gerando_cloudformation(self, resource):
        template = Template()
        template.add_resource(resource)
        resource_json = json.loads(template.to_json())
        return resource_json

    def test_deve_retornar_um_codebuild_customizado_com_imagem_definica(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild(params['nome'], params['env'], imagecustom='python', buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        print(codebuild)
        assert  'python' == codebuild['Resources']['Testecodebuild']['Properties']['Environment']['Image']

    def test_deve_retornar_um_codebuild_customizado_sem_imagem_definica(self, params):
        codebuild  = NewCodeBuild(params['role'])
        image_com_espaco = codebuild.create_codebuild(params['nome'], params['env'], imagecustom="", buildspec=False,)
        image_com_false = codebuild.create_codebuild(params['nome'], params['env'], imagecustom=False, buildspec=False )

        code_com_espaco = self.gerando_cloudformation(image_com_espaco)
        code_com_false = self.gerando_cloudformation(image_com_false)
        print(code_com_espaco)
        print(code_com_false)
        assert 'aws/codebuild/standard:2.0' == code_com_espaco['Resources']['Testecodebuild']['Properties']['Environment']['Image']
        assert 'aws/codebuild/standard:2.0' == code_com_false['Resources']['Testecodebuild']['Properties']['Environment']['Image']

    def test_deve_retornar_um_codebuild_customizado_com_buildspec_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec = codebuild.create_codebuild(params['nome'], params['env'], imagecustom=False, buildspec='test_buildspec.yml')

        code_buildspec  = self.gerando_cloudformation(codebuild_com_buildspec)
        print(code_buildspec)
        assert "test_buildspec.yml" in code_buildspec['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_um_codebuild_customizado_sem_buildspec_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec_espaco = codebuild.create_codebuild(params['nome'], params['env'], imagecustom=False, buildspec='')
        codebuild_com_buildspec_false = codebuild.create_codebuild(params['nome'], params['env'], imagecustom=False,buildspec=False)

        buildspec_espaco = self.gerando_cloudformation(codebuild_com_buildspec_espaco)
        buildspec_false = self.gerando_cloudformation(codebuild_com_buildspec_false)
        assert "pipeline/testecodebuild_buildspec.yml" in buildspec_espaco['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']
        assert "pipeline/testecodebuild_buildspec.yml" in buildspec_false['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_um_codebuild_customizado_com_env_definido(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild(params['nome'], params['env'], imagecustom=False, buildspec=False)
        codebuild = self.gerando_cloudformation(codeobject)

        for env in params['env']:
            assert env in codebuild['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']

    def test_deve_retornar_um_codebuild_customizado_sem_env_definido(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild(params['nome'], '', imagecustom=False, buildspec=False)
        codeobject_vazio = libcodebuild.create_codebuild(params['nome'], [], imagecustom=False, buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        codebuild_vazio = self.gerando_cloudformation(codeobject_vazio)

        assert len(codebuild['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0
        assert len(codebuild_vazio['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0

    def test_deve_retornar_um_codebuild_customizado_com_env_definido_errado(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild(params['nome'], ['10','20'], imagecustom=False, buildspec=False)
        codeobject_dict = libcodebuild.create_codebuild(params['nome'], [{'var1':'var1'}, {'var2':'var2'}], imagecustom=False, buildspec=False)
        codeobject_dict_name = libcodebuild.create_codebuild(params['nome'], [{'Name':'var1'}, {'Name':'var2'}], imagecustom=False, buildspec=False)
        codeobject_dict_value = libcodebuild.create_codebuild(params['nome'], [{'Value': 'var1'}, {'Value': 'var2'}],imagecustom=False, buildspec=False)
        codebuild = self.gerando_cloudformation(codeobject)
        codebuild_dict = self.gerando_cloudformation(codeobject_dict)
        codebuild_dict_name = self.gerando_cloudformation(codeobject_dict_name)
        codebuild_dict_value = self.gerando_cloudformation(codeobject_dict_value)

        assert len(codebuild['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0
        assert len(codebuild_dict['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0
        assert len(codebuild_dict_name['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0
        assert len(codebuild_dict_value['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0

    def test_deve_retornar_um_codebuild_customizado_quando_nome_codebuild_tiver_alphanumerico(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild('Teste-codebuild', params['env'], imagecustom='python', buildspec=False)
        codeobject_ = libcodebuild.create_codebuild('Teste_codebuild', params['env'], imagecustom='python',buildspec=False)
        codeobject__ = libcodebuild.create_codebuild('Teste$codebuild', params['env'], imagecustom='python',buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        codebuild_ = self.gerando_cloudformation(codeobject_)
        codebuild__ = self.gerando_cloudformation(codeobject__)

        print(codebuild)
        print(codebuild_)
        print(codebuild__)
        assert 'TesteCodebuild' in codebuild['Resources']
        assert 'Testecodebuild' in codebuild_['Resources']
        assert 'Testecodebuild' in codebuild__['Resources']

    def test_deve_retornar_codebuild_do_ControlVersion(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.ControlVersion(featurename='pipeline', microservicename='teste', runtime=runtime,branchname='develop', custom=False)
            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-ControlVersion-develop' in cf['Resources']['PipelineTesteControlversionDevelop']['Properties']['Name']
            assert 'common/controlversion/buildspec.yml' in cf['Resources']['PipelineTesteControlversionDevelop']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteControlversionDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Sast(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            sast = newcodebuild.BuildSAST(featurename='pipeline', microservicename='teste', runtime=runtime, branchname='develop', custom=False)
            cf = self.gerando_cloudformation(sast)
            print(cf)
            assert 'pipeline-teste-BuildSAST-develop' in cf['Resources']['PipelineTesteBuildsastDevelop']['Properties']['Name']
            assert f'../01/{runtime}/sast/buildspec.yml' in cf['Resources']['PipelineTesteBuildsastDevelop']['Properties']['Source']['BuildSpec']
            assert '984688426935.dkr.ecr.sa-east-1.amazonaws.com/appsec:latest' in cf['Resources']['PipelineTesteBuildsastDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_TestUnit_sem_builcustomizado(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])

            codebuild = newcodebuild.BuildTestUnit(featurename='pipeline', microservicename='teste', runtime=runtime,branchname='develop', custom=False)
            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-BuildTestUnit-develop' in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Name']
            assert f"../01/{runtime}/testunit/buildspec.yml" in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_TestUnit_com_builcustomizado(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.BuildTestUnit(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=True)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-BuildTestUnit-develop' in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Name']
            assert "pipeline/buildspec_testunit.yml" in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteBuildtestunitDevelop']['Properties']['Environment']['Image']


    def test_deve_retornar_codebuild_do_Sonar(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            sonar = newcodebuild.Sonar(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=False)
            cf = self.gerando_cloudformation(sonar)
            print(cf)
            assert 'pipeline-teste-Sonar-develop' in cf['Resources']['PipelineTesteSonarDevelop']['Properties']['Name']
            assert f'../01/{runtime}/sonarqube/buildspec.yml' in cf['Resources']['PipelineTesteSonarDevelop']['Properties']['Source']['BuildSpec']
            assert '049557819541.dkr.ecr.sa-east-1.amazonaws.com/codebuild-sonar:latest' in cf['Resources']['PipelineTesteSonarDevelop']['Properties']['Environment']['Image']


    def test_deve_retornar_codebuild_do_Build_sem_builcustomizado(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.Build(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=False)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-Build-develop' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Name']
            assert f'../01/{runtime}/build/buildspec.yml' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Build_com_builcustomizado(self, params):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.Build(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=True)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-Build-develop' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Name']
            assert 'pipeline/buildspec_build.yml' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteBuildDevelop']['Properties']['Environment']['Image']


    def test_deve_retornar_codebuild_do_Aqua(self, params):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.Aqua(featurename='pipeline', microservicename='teste', branchname='develop', custom=True)

        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-Aqua-develop' in cf['Resources']['PipelineTesteAquaDevelop']['Properties']['Name']
        assert '/common/aqua/buildspec.yml' in cf['Resources']['PipelineTesteAquaDevelop']['Properties']['Source']['BuildSpec']
        assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteAquaDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_deploy_ecs(self, params):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.DeployECS(featurename='pipeline', microservicename='teste', branchname='develop')
        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-DeployECS-develop' in cf['Resources']['PipelineTesteDeployecsDevelop']['Properties']['Name']
        assert '/common/deploy/buildspec_ecs.yml' in cf['Resources']['PipelineTesteDeployecsDevelop']['Properties']['Source']['BuildSpec']
        assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTesteDeployecsDevelop']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Publish_ECR(self, params):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.PublishECR(featurename='pipeline', microservicename='teste', branchname='develop')

        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-PublishECR-develop' in cf['Resources']['PipelineTestePublishecrDevelop']['Properties']['Name']
        assert '/common/publish/buildspec_ecr.yml' in cf['Resources']['PipelineTestePublishecrDevelop']['Properties']['Source']['BuildSpec']
        assert 'aws/codebuild/standard:2.0' in cf['Resources']['PipelineTestePublishecrDevelop']['Properties']['Environment']['Image']
