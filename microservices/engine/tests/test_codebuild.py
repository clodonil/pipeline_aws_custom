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

    def gerando_cloudformation(self, resource):
        template = Template()
        template.add_resource(resource)
        resource_json = json.loads(template.to_json())
        return resource_json

    def test_deve_retornar_um_codebuild_customizado_com_imagem_definica(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom='python', buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        print(codebuild)
        assert  'python' == codebuild['Resources']['Testecodebuild']['Properties']['Environment']['Image']

    def test_deve_retornar_um_codebuild_customizado_sem_imagem_definica(self, params):
        codebuild  = NewCodeBuild(params['role'])
        image_com_espaco = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom="", buildspec=False,)
        image_com_false = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom=False, buildspec=False )

        code_com_espaco = self.gerando_cloudformation(image_com_espaco)
        code_com_false = self.gerando_cloudformation(image_com_false)
        print(code_com_espaco)
        print(code_com_false)
        assert 'aws/codebuild/standard:2.0' == code_com_espaco['Resources']['Testecodebuild']['Properties']['Environment']['Image']
        assert 'aws/codebuild/standard:2.0' == code_com_false['Resources']['Testecodebuild']['Properties']['Environment']['Image']

    def test_deve_retornar_um_codebuild_customizado_com_cache_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], cache=True)

        code_buildspec  = self.gerando_cloudformation(codebuild_com_buildspec)
        print(code_buildspec)
        assert 'Cache' in code_buildspec['Resources']['Testecodebuild']['Properties']
        assert 'S3' in code_buildspec['Resources']['Testecodebuild']['Properties']['Cache']['Type']
        assert '!Sub ${AWS::AccountId}-cache' in code_buildspec['Resources']['Testecodebuild']['Properties']['Cache']['Location']

    def test_deve_retornar_um_codebuild_customizado_sem_cache_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], cache=False)

        code_buildspec  = self.gerando_cloudformation(codebuild_com_buildspec)
        print(code_buildspec)
        assert 'Cache' not in code_buildspec['Resources']['Testecodebuild']['Properties']

    def test_deve_retornar_um_codebuild_customizado_com_buildspec_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom=False, buildspec='test_buildspec.yml')

        code_buildspec  = self.gerando_cloudformation(codebuild_com_buildspec)
        print(code_buildspec)
        assert "test_buildspec.yml" in code_buildspec['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_um_codebuild_customizado_sem_buildspec_definido(self, params):
        codebuild  = NewCodeBuild(params['role'])
        codebuild_com_buildspec_espaco = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom=False, buildspec='')
        codebuild_com_buildspec_false = codebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom=False,buildspec=False)

        buildspec_espaco = self.gerando_cloudformation(codebuild_com_buildspec_espaco)
        buildspec_false = self.gerando_cloudformation(codebuild_com_buildspec_false)
        assert "pipeline/buildspec_testecodebuild.yml" in buildspec_espaco['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']
        assert "pipeline/buildspec_testecodebuild.yml" in buildspec_false['Resources']['Testecodebuild']['Properties']['Source']['BuildSpec']

    def test_deve_retornar_um_codebuild_customizado_com_env_definido(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild('Testecodebuild',params['nome'], params['env'], imagecustom=False, buildspec=False)
        codebuild = self.gerando_cloudformation(codeobject)

        for env in params['env']:
            assert env in codebuild['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']

    def test_deve_retornar_um_codebuild_customizado_sem_env_definido(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild('Testecodebuild',params['nome'], '', imagecustom=False, buildspec=False)
        codeobject_vazio = libcodebuild.create_codebuild('Testecodebuild',params['nome'], [], imagecustom=False, buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        codebuild_vazio = self.gerando_cloudformation(codeobject_vazio)

        assert len(codebuild['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0
        assert len(codebuild_vazio['Resources']['Testecodebuild']['Properties']['Environment']['EnvironmentVariables']) == 0

    def test_deve_retornar_um_codebuild_customizado_com_env_definido_errado(self, params):
        libcodebuild  = NewCodeBuild(params['role'])
        codeobject = libcodebuild.create_codebuild('Testecodebuild', params['nome'], ['10','20'], imagecustom=False, buildspec=False)
        codeobject_dict = libcodebuild.create_codebuild('Testecodebuild',params['nome'], [{'var1':'var1'}, {'var2':'var2'}], imagecustom=False, buildspec=False)
        codeobject_dict_name = libcodebuild.create_codebuild('Testecodebuild',params['nome'], [{'Name':'var1'}, {'Name':'var2'}], imagecustom=False, buildspec=False)
        codeobject_dict_value = libcodebuild.create_codebuild('Testecodebuild',params['nome'], [{'Value': 'var1'}, {'Value': 'var2'}],imagecustom=False, buildspec=False)
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
        codeobject = libcodebuild.create_codebuild('TesteCodebuild','Teste-codebuild', params['env'], imagecustom='python', buildspec=False)
        codeobject_ = libcodebuild.create_codebuild('TesteCodebuild','Teste_codebuild', params['env'], imagecustom='python',buildspec=False)
        codeobject__ = libcodebuild.create_codebuild('TesteCodebuild','Teste$codebuild', params['env'], imagecustom='python',buildspec=False)

        codebuild = self.gerando_cloudformation(codeobject)
        codebuild_ = self.gerando_cloudformation(codeobject_)
        codebuild__ = self.gerando_cloudformation(codeobject__)

        print(codebuild)
        print(codebuild_)
        print(codebuild__)
        assert 'TesteCodebuild' in codebuild['Resources']
        assert 'TesteCodebuild' in codebuild_['Resources']
        assert 'TesteCodebuild' in codebuild__['Resources']

    def test_deve_retornar_codebuild_do_ControlVersion(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.ControlVersion(featurename='pipeline', microservicename='teste', runtime=runtime,branchname='develop', custom=False, imageCustom=imageCustom)
            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-controlversion-develop' in cf['Resources']['ControlVersion']['Properties']['Name']
            assert 'common/controlversion/buildspec.yml' in cf['Resources']['ControlVersion']['Properties']['Source']['BuildSpec']
            assert 'aws/codebuild/standard:2.0' in cf['Resources']['ControlVersion']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Sast(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            sast = newcodebuild.Fortify(featurename='pipeline', microservicename='teste', runtime=runtime, branchname='develop', custom=False,imageCustom=imageCustom)
            cf = self.gerando_cloudformation(sast)
            print(cf)
            assert 'pipeline-teste-fortify-develop' in cf['Resources']['Fortify']['Properties']['Name']
            assert f'../01/{runtime}/sast/buildspec.yml' in cf['Resources']['Fortify']['Properties']['Source']['BuildSpec']
            assert 'imagem_sast' in cf['Resources']['Fortify']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_TestUnit_sem_builcustomizado(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])

            codebuild = newcodebuild.TestUnit(featurename='pipeline', microservicename='teste', runtime=runtime,branchname='develop', custom=False, imageCustom=imageCustom)
            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-testunit-develop' in cf['Resources']['TestUnit']['Properties']['Name']
            assert f"../01/{runtime}/testunit/buildspec.yml" in cf['Resources']['TestUnit']['Properties']['Source']['BuildSpec']
            assert 'imagem_TestUnit' in cf['Resources']['TestUnit']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_TestUnit_com_builcustomizado(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.TestUnit(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=True, imageCustom=imageCustom)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-testunit-develop' in cf['Resources']['TestUnit']['Properties']['Name']
            assert "pipeline/buildspec_testunit.yml" in cf['Resources']['TestUnit']['Properties']['Source']['BuildSpec']
            assert 'imagem_TestUnit' in cf['Resources']['TestUnit']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Sonar(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            sonar = newcodebuild.Sonar(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=False, imageCustom=imageCustom)
            cf = self.gerando_cloudformation(sonar)
            print(cf)
            assert 'pipeline-teste-sonar-develop' in cf['Resources']['Sonar']['Properties']['Name']
            assert f'../01/{runtime}/sonarqube/buildspec.yml' in cf['Resources']['Sonar']['Properties']['Source']['BuildSpec']
            assert 'imagem_sonar' in cf['Resources']['Sonar']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Build_sem_builcustomizado(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.Build(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=False, imageCustom=imageCustom)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-build-develop' in cf['Resources']['Build']['Properties']['Name']
            assert f'../01/{runtime}/build/buildspec.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert 'image_Build' in cf['Resources']['Build']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Build_com_builcustomizado(self, params, imageCustom):
        for runtime in params['runtime']:
            newcodebuild =  NewCodeBuild(params['role'])
            codebuild = newcodebuild.Build(featurename='pipeline', microservicename='teste', runtime=runtime,
                                                   branchname='develop', custom=True, imageCustom=imageCustom)

            cf = self.gerando_cloudformation(codebuild)
            print(cf)
            assert 'pipeline-teste-build-develop' in cf['Resources']['Build']['Properties']['Name']
            assert 'pipeline/buildspec_build.yml' in cf['Resources']['Build']['Properties']['Source']['BuildSpec']
            assert 'image_Build' in cf['Resources']['Build']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Aqua(self, params, imageCustom):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.Aqua(runtime='python',featurename='pipeline', microservicename='teste', branchname='develop', custom=True, imageCustom=imageCustom)

        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-aqua-develop' in cf['Resources']['Aqua']['Properties']['Name']
        assert '/common/container-security/buildspec.yml' in cf['Resources']['Aqua']['Properties']['Source']['BuildSpec']
        assert 'imagem_Aqua' in cf['Resources']['Aqua']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_deploy_ecs(self, params, imageCustom):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.DeployECSDev(runtime='python', featurename='pipeline', microservicename='teste', branchname='develop', imageCustom=imageCustom)
        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-deployecs-develop' in cf['Resources']['DeployECSDev']['Properties']['Name']
        assert '/common/deploy/buildspec_ecs.yml' in cf['Resources']['DeployECSDev']['Properties']['Source']['BuildSpec']
        assert 'aws/codebuild/standard:2.0' in cf['Resources']['DeployECSDev']['Properties']['Environment']['Image']

    def test_deve_retornar_codebuild_do_Publish_ECR(self, params, imageCustom):
        newcodebuild =  NewCodeBuild(params['role'])
        codebuild = newcodebuild.PublishECRDev(runtime='python' , featurename='pipeline', microservicename='teste', branchname='develop', imageCustom=imageCustom)

        cf = self.gerando_cloudformation(codebuild)
        print(cf)
        assert 'pipeline-teste-publishecr-develop' in cf['Resources']['PublishECRDev']['Properties']['Name']
        assert '/common/Publish/buildspec-to-dev.yml' in cf['Resources']['PublishECRDev']['Properties']['Source']['BuildSpec']
        assert 'aws/codebuild/standard:2.0' in cf['Resources']['PublishECRDev']['Properties']['Environment']['Image']
