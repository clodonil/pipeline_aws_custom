from templates.codepipeline.pipeline import NewPipeline
from troposphere import Template
import pytest
import json


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
                }
        }
        return actions

    def gerando_cloudformation(self, resource):
        template = Template()
        template.add_resource(resource)
        resource_json = json.loads(template.to_json())
        return resource_json

    def test_deve_retornar_um_Action_tipo_source(self, params):
        action = params['source']
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Source' == cf['Resources'][action['name']]['ActionTypeId']['Category']
        assert 'CodeCommit' == cf['Resources'][action['name']]['ActionTypeId']['Provider']
        assert 'source' in cf['Resources']
        assert 1 == cf['Resources']['source']['RunOrder']

    def test_deve_retornar_um_Action_tipo_source_Nome_Alphanumerico(self, params):
        action = params['source']
        name = 'Source-App'
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(name, action['runorder'], action['configuration'], action['type'], action['role'])
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Source' == cf['Resources']['SourceApp']['ActionTypeId']['Category']
        assert 'CodeCommit' == cf['Resources']['SourceApp']['ActionTypeId']['Provider']
        assert 'SourceApp' in cf['Resources']
        assert 1 == cf['Resources']['SourceApp']['RunOrder']
        assert 'arn:aws:iam::033921349789:role/RoleCodepipelineRole' == cf['Resources']['SourceApp']['RoleArn']

    def test_deve_retornar_um_Action_tipo_source_Sem_Role(self, params):
        action = params['source']
        name = 'Source-App'
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(name, action['runorder'], action['configuration'], action['type'], role='')
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Source' == cf['Resources']['SourceApp']['ActionTypeId']['Category']
        assert 'CodeCommit' == cf['Resources']['SourceApp']['ActionTypeId']['Provider']
        assert 'SourceApp' in cf['Resources']
        assert 1 == cf['Resources']['SourceApp']['RunOrder']


    def test_deve_retornar_um_Action_tipo_Build(self, params):
        action = params['action']
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Build' == cf['Resources']['compilar']['ActionTypeId']['Category']
        assert 'CodeBuild' == cf['Resources']['compilar']['ActionTypeId']['Provider']
        assert 'compilar' in cf['Resources']
        assert 1 == cf['Resources']['compilar']['RunOrder']

    def test_deve_retornar_um_Action_tipo_Build_Multiplos_Sources(self, params):
        action = params['action']
        configuration = {'ProjectName' : 'proj','PrimarySource' : 'App', 'InputArtifacts': ['App','App2'], 'runorder': '1'}
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(action['name'], action['runorder'], configuration, action['type'], action['role'])
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Build' == cf['Resources']['compilar']['ActionTypeId']['Category']
        assert 'CodeBuild' == cf['Resources']['compilar']['ActionTypeId']['Provider']
        assert 'compilar' in cf['Resources']
        assert 1 == cf['Resources']['compilar']['RunOrder']
        assert 'App' in [input['Name'] for input in cf['Resources']['compilar']['InputArtifacts']]
        assert 'App2' in [input['Name'] for input in cf['Resources']['compilar']['InputArtifacts']]

    def test_deve_retornar_um_Action_tipo_Build_Nome_Alphanumerico(self, params):
        action = params['action']
        name = 'Build-App'
        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(name, action['runorder'], action['configuration'], action['type'], action['role'])
        cf = self.gerando_cloudformation(cf_action)
        print(cf)

        assert 'Build' == cf['Resources']['BuildApp']['ActionTypeId']['Category']
        assert 'CodeBuild' == cf['Resources']['BuildApp']['ActionTypeId']['Provider']
        assert 'BuildApp' in cf['Resources']
        assert 1 == cf['Resources']['BuildApp']['RunOrder']

    def test_deve_retornar_um_stage(self, params):
        action = params['action']
        stage  = params['stage']

        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf_stage  = pipeline.create_stage(stage['name'], [cf_action])
        cf = self.gerando_cloudformation(cf_stage)
        print(cf)

        assert 'Compilador' in cf['Resources']
        assert 'Compilador' == cf['Resources']['Compilador']['Name']

    def test_deve_retornar_um_stage_Com_Nome_Alphanumerico(self, params):
        action = params['action']
        name = 'Stage-Compilacao'

        pipeline  = NewPipeline()
        cf_action = pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf_stage  = pipeline.create_stage(name, [cf_action])
        cf = self.gerando_cloudformation(cf_stage)
        print(cf)

        assert 'StageCompilacao' in cf['Resources']
        assert 'Stage-Compilacao' == cf['Resources']['StageCompilacao']['Name']

    def test_deve_retornar_uma_pipeline(self, params):
        action = params['action']
        stage  = params['stage']
        pipeline = params['pipeline']


        obj_pipeline  = NewPipeline()
        cf_action = obj_pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf_stage  = obj_pipeline.create_stage(stage['name'], [cf_action])
        cf_pipeline = obj_pipeline.create_pipeline(pipeline['name'], pipeline['role'], [cf_stage])

        cf = self.gerando_cloudformation(cf_pipeline)
        print(cf)

        assert 'PipelineEcsreports' in cf['Resources']
        assert 'Pipelineecs' in cf['Resources']
        assert 'pipelineecs' in cf['Resources']['PipelineEcsreports']['Properties']['BucketName']

    def test_deve_retornar_um_Bucket_S3_para_pipeline(self, params):
        action = params['action']
        stage  = params['stage']
        pipeline = params['pipeline']


        obj_pipeline  = NewPipeline()
        cf_action = obj_pipeline.create_action(action['name'], action['runorder'], action['configuration'], action['type'], action['role'])
        cf_stage  = obj_pipeline.create_stage(stage['name'], [cf_action])
        cf_pipeline = obj_pipeline.create_pipeline(pipeline['name'], pipeline['role'], [cf_stage])

        cf = self.gerando_cloudformation(cf_pipeline)
        print(cf)

        assert 'pipelineecs' in cf['Resources']['PipelineEcsreports']['Properties']['BucketName']