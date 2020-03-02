from troposphere import Parameter, Ref, Template
from engine.codepipeline.pipeline import NewPipeline
from engine.codebuild.newcodebuild import NewCodeBuild

template = Template()

codebuild = NewCodeBuild('arn:aws:iam::033921349789:role/RoleCodeBuildRole', 'aaa:aaa:aa','vpc-bb0436c1','subnet-035ab95c','subnet-4c518942', 'sg-56391a7c')
ci  = codebuild.ci('python37')
publish  = codebuild.Publish_ECR()
deploy   = codebuild.Deploy_ECS()

for code in ci:
    template.add_resource(code)

template.add_resource(publish)

template.add_resource(deploy)

pipeline_app_ecs = NewPipeline()

#action
configuration = {'BranchName': 'master','RepositoryName' : 'teste'}
action_source = pipeline_app_ecs.create_action('SourceApp', "1",configuration, 'Source')

                                                                                  
configuration = {'ProjectName' : 'CODEBUILDteste','PrimarySource' : 'SourceApp', 'InputArtifacts': 'SourceApp'}    
action_build = pipeline_app_ecs.create_action('Build', "1",configuration, 'Build')
action_testunit = pipeline_app_ecs.create_action('TestUnit', "1",configuration, 'Build')
action_sast = pipeline_app_ecs.create_action('Sast', "1",configuration, 'Build')
action_sonar = pipeline_app_ecs.create_action('Sonar', "1",configuration, 'Build')
action_aqua = pipeline_app_ecs.create_action('Aqua', "2",configuration, 'Build')
action_publish = pipeline_app_ecs.create_action('Publish', "1",configuration, 'Build')
action_deploy = pipeline_app_ecs.create_action('Deploy', "1",configuration, 'Build')

#Stage
stage_source = pipeline_app_ecs.create_stage('Source', [action_source])
stage_ci = pipeline_app_ecs.create_stage('CI', [action_build, action_testunit, action_sast, action_sonar, action_aqua])
stage_publish = pipeline_app_ecs.create_stage('Publish', [action_publish])
stage_deploy = pipeline_app_ecs.create_stage('Deploy', [action_deploy])


#Pipelin
new_pipeline = pipeline_app_ecs.create_pipeline('PipelineTest','arn:aws:iam::033921349789:role/RoleCodepipelineRole', [stage_source,stage_ci, stage_publish, stage_deploy])
template.add_resource(new_pipeline[0])
template.add_resource(new_pipeline[1])
print(template.to_json())