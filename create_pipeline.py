from troposphere import Parameter, Ref, Template
from codepipeline.pipeline import NewPipeline
from codebuild.custom.codebuild_custom import Custom

template = Template()

pipeline1 = Custom('RolePipeline', 'aaa:aaa:aa','vpc-2f09a348','sunet1','subnet2', 'sg-51530134')
codebuild1  = pipeline1.create_codebuild('Teste1', {'chave1':'valor1'}, 'linuxdockerhub')
codebuild2  = pipeline1.create_codebuild('Teste2', {'chave2':'valor1'},)

template.add_resource(codebuild1)
template.add_resource(codebuild2)




demo = NewPipeline()

#action
configuration = {'BranchName': 'master','RepositoryName' : 'teste'}
source = demo.create_action('SourceApp', "1",configuration, 'Source')


configuration = {'ProjectName' : 'CODEBUILDteste','PrimarySource' : 'SourceApp'}    
build = demo.create_action('TestUnit', "1",configuration, 'Build')

#Stage
source = demo.create_stage('Source', [source])
test = demo.create_stage('Teste', [build])

#Pipeline

new_pipeline = demo.create_pipeline('PipelineTest','arnrole', [source,test])
template.add_resource(new_pipeline)

print(template.to_json())