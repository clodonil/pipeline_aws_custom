from troposphere import Parameter, Ref, Template
from codepipeline.pipeline import NewPipeline
from codebuild.newcodebuild import NewCodeBuild




class NewTemplate:
    def __init__(self, template):
        self.template = template        
        self.role = 'arn:aws:iam::033921349789:role/RoleCodeBuildRole'
        self.vpc = 'vpc-bb0436c1'
        self.subnet1 = 'subnet-035ab95c'
        self.subnet2 = 'subnet-4c518942'
        self.sg = 'sg-56391a7c'

    def app_ecs(self, runtime, env, stages):
        template = Template()
        list_codebuild = []
        pipeline_stages = {
            'source' : ['source0'],
            'ci' : ['SAST', 'SONAR', 'TestUnit', 'Build'],
            'security' : ['Aqua'],
            'publish' : ['PublishECR']
        }

        codebuild = NewCodeBuild(self.role, 'aaa:aaa:aa',self.vpc,self.subnet1,self.subnet2, self.sg)
        
        for t_codebuild in stages:
          if isinstance(t_codebuild, str):            
             list_codebuild.extend(codebuild.new_app_ecs(t_codebuild, runtime, env)) 

          if isinstance(t_codebuild, dict):
             name_custom_stage = list(t_codebuild.keys())[0]
             custom = name_custom_stage.split('::')
                
             if len(custom) > 1:
                for list_yaml in t_codebuild[name_custom_stage]:
                    temp_name = list(list_yaml.keys())[0]
                    imagemcustom = False
                                            
                    for params in list_yaml[temp_name]:
                        if 'source' in params:
                            source = params['source']
                        elif 'runorder' in params:
                            runorder = params['runorder']
                        elif 'imagecustom' in params:    
                            imagemcustom = params['imagecustom']
                    
                
                    pipeline_stages[custom[0]].append(temp_name)                    
                    list_codebuild.extend([codebuild.create_codebuild(temp_name, env, imagemcustom)])
                
                #Adicionando os codebuild do padrao    
                list_codebuild.extend(codebuild.new_app_ecs(custom[0],runtime, env))
                                      
        
        pipeline_app_ecs = NewPipeline()
        action = {}

        #Source         
        configuration = {'BranchName': 'master','RepositoryName' : 'teste'}
        action['source0'] = pipeline_app_ecs.create_action('SourceApp', "1",configuration, 'Source')
      
        for code in list_codebuild:
            template.add_resource(code)            
            title = code.title          
      
            configuration = {'ProjectName' : title,'PrimarySource' : 'SourceApp', 'InputArtifacts': 'SourceApp'}    
            action[title] = pipeline_app_ecs.create_action(title, "1",configuration, 'Build')
        
        #Stage
        stages = []
        for action_stage in pipeline_stages:
    
             add_stage = []             
             for acao in pipeline_stages[action_stage]:
                 add_stage.append(action[acao])
                 stages.append(pipeline_app_ecs.create_stage('Source', add_stage))


        #Pipeline
        new_pipeline = pipeline_app_ecs.create_pipeline('PipelineTest','arn:aws:iam::033921349789:role/RoleCodepipelineRole', stages)
        template.add_resource(new_pipeline[0])
        template.add_resource(new_pipeline[1])
        return template.to_json()