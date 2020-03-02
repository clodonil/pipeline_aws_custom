from troposphere import Parameter, Ref, Template
from codepipeline.pipeline import NewPipeline
from codebuild.ci.codebuild_ci import CI

template = Template()

pipeline1 = CI('RolePipeline', 'aaa:aaa:aa','vpc-2f09a348','sunet1','subnet2', 'sg-51530134')
codebuilds  = pipeline1.create('python37')

print(codebuilds)

for codebuild in codebuilds:
    template.add_resource(codebuild)


#demo = NewPipeline()

#action
#configuration = {'BranchName': 'master','RepositoryName' : 'teste'}
#source = demo.create_action('SourceApp', "1",configuration, 'Source')


#configuration = {'ProjectName' : 'CODEBUILDteste','PrimarySource' : 'SourceApp'}    
#build = demo.create_action('TestUnit', "1",configuration, 'Build')

#Stage
#source = demo.create_stage('Source', [source])
#test = demo.create_stage('Teste', [build])

#Pipeline
#new_pipeline = demo.create_pipeline('PipelineTest','arnrole', [source,test])
#template.add_resource(new_pipeline)

print(template.to_json())