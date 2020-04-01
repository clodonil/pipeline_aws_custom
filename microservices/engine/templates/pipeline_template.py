from troposphere import Template
from templates.codepipeline.pipeline import NewPipeline
from templates.codebuild.newcodebuild import NewCodeBuild
from tools.dynamodb import DyConnect
from tools.config import aws_region, dynamodb
import os

class NewTemplate:
    def __init__(self, template, codepipeline_role, codebuild_role):
        self.template = template        
        self.codepipeline_role = codepipeline_role
        self.codebuild_role = codebuild_role
        self.vpc = 'vpc-bb0436c1'
        self.subnet1 = 'subnet-035ab95c'
        self.subnet2 = 'subnet-4c518942'
        self.sg = 'sg-56391a7c'

    def get_dy_template(self, template_name):
        newtemplate = DyConnect(dynamodb['template'],aws_region)
        query = {'name':template_name}
        stages = newtemplate.dynamodb_query(query)

        if 'Item' in stages:
            if 'details' in stages['Item']:
                  return stages['Item']['details']

        return False        

    def generate_codebuild(self, runtime, pipeline_template, stages):
        list_codebuild = []
        
        codebuild = NewCodeBuild(self.codebuild_role, 'aaa:aaa:aa',self.vpc,self.subnet1,self.subnet2, self.sg)
        cont_stage = 0
        action_custom = 1
        
        for t_codebuild in stages:
          stage_custom_used = False
          if isinstance(t_codebuild, str):
             t_build_template =  [ item for item in pipeline_template if item.split('-')[1] == t_codebuild ][0] 
             if t_codebuild != 'source': 
                for l_codebuild_template in pipeline_template[t_build_template]:
                    for g_codebuild in l_codebuild_template:
                       new_codebuild  =  eval('codebuild.' + g_codebuild +'(runtime)')                    
                       list_codebuild.append(new_codebuild)

          elif isinstance(t_codebuild, dict):
             name_custom_stage = list(t_codebuild.keys())[0]
             custom = name_custom_stage.split('::')             
             stages_temp =[]
             
             # Customizando o action
             if custom[-1] == 'custom' and custom[0] != 'source':
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
                        elif 'environment' in params:
                            env = {}
                            for dic_params in params['environment']:
                                env.update(dic_params)                        

                    configuration = {temp_name:{'ProjectName' : temp_name,'PrimarySource' : source, 'InputArtifacts': source, 'runorder': str(runorder)}}                    
                    stages_temp.append(configuration)                    
                    list_codebuild.append(codebuild.create_codebuild(temp_name, env, imagemcustom))
                
                #Adicionando os codebuild do padrao
                if t_codebuild != 'source':
                   t_build_template =  [ item for item in pipeline_template if item.split('-')[1] == custom[0]][0]                                
                   for l_codebuild_template in pipeline_template[t_build_template]:
                     for g_codebuild in l_codebuild_template:                         
                         new_codebuild  =  eval('codebuild.' + g_codebuild +'(runtime)')                    
                         list_codebuild.append(new_codebuild)
                   pipeline_template[t_build_template].extend(stages_temp)
             
             # Customizando o stage      
             elif custom[0] == 'custom':
                stage_custom_used = True 
                stage_name = f'{cont_stage}.{action_custom}-{custom[1]}'
                action_custom +=1
                pipeline_template[stage_name] =[]
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
                        elif 'environment' in params:
                            env = {}
                            for dic_params in params['environment']:
                                env.update(dic_params)                        
                    
                    configuration = {temp_name:{'ProjectName' : temp_name,'PrimarySource' : source, 'InputArtifacts': source, 'runorder': str(runorder)}}
                    stages_temp.append(configuration)                    
                    list_codebuild.append(codebuild.create_codebuild(temp_name, env, imagemcustom))                
                pipeline_template[stage_name].extend(stages_temp)

          if not stage_custom_used:
             cont_stage +=1
        
        return list_codebuild

    def generate_template(self, resources ):
        template = Template()
        for resource in resources:
            template.add_resource(resource)
        return template.to_json()    

    def generate_sources(self, stages, env, params):
        action = {}
        pipeline = NewPipeline()

        configuration = {'BranchName': 'release-1','RepositoryName' : 'sharedlibrary'}
        action['source'] = [pipeline.create_action('SharedLibrary', "1",configuration, 'Source')]

        for t_codebuild in stages:
            if 'source' in t_codebuild or 'source::custom' in t_codebuild:

               if t_codebuild == 'source':
                  configuration ={'RepositoryName' : params['Projeto'], 'BranchName': env}
               if 'source::custom' in t_codebuild:
                  for config in t_codebuild['source::custom']:
                      configuration.update(config)
                  if not 'BranchName' in configuration:
                      configuration.update({'BranchName': env})
               action['source'].append(pipeline.create_action(configuration['RepositoryName'], "1",configuration, 'Source'))

        return action

    def generate_action(self, list_codebuild, pipeline_template, params):
        pipeline = NewPipeline()
        action ={}
        
        for code in list_codebuild:        
          title = code.title          
          for k in pipeline_template:
            for t in pipeline_template[k]:
              if title in t:                   
                configuration = t[title]
          configuration['PrimarySource'] = params['Projeto']
          configuration['InputArtifacts'] = params['Projeto']
          runorder = configuration.pop('runorder')
          configuration['ProjectName'] = title
          action[title] = pipeline.create_action(title, int(runorder) ,configuration, 'Build')
        
        return action  

    def generate_stage(self, pipeline_stages, list_action):
        pipeline = NewPipeline()
        stages = []
        
        for t_stage in sorted(pipeline_stages):            
            control_stage = t_stage.split('-')[1]            
            if control_stage == 'source':
               l_stage=[]
               for stg in list_action[control_stage]:
                   l_stage.append(stg)
               stages.append(pipeline.create_stage('Source', l_stage))
            else:
                l_stage=[]
                for stg in pipeline_stages[t_stage]:
                    for name_stg in stg:                    
                      l_stage.append(list_action[name_stg])
                stages.append(pipeline.create_stage(control_stage, l_stage)) 
        
        return stages            

    def generate_pipeline(self, list_stages, projeto):
        pipeline = NewPipeline()
        resource = pipeline.create_pipeline(projeto, self.codepipeline_role, list_stages)
        return resource

    def save_swap(self, projeto, template, env):
        path = 'swap'
        if not os.path.isdir(path):
           os.mkdir(path)
        if os.path.isdir(path):
           filename = f'{path}/{projeto}-{env}.json'
           print(filename)
           with open(filename, 'w') as file:
             file.write(template)
        return filename

    def generate(self, runtime, env, stages, template_name, params):
        resources = []
        list_action = {}
        pipeline_stages = self.get_dy_template(template_name)

        # create codebuild
        list_codebuild = self.generate_codebuild(runtime, pipeline_stages, stages )

        # create action
        list_action.update(self.generate_sources(stages, env, params))
        list_action.update(self.generate_action(list_codebuild, pipeline_stages, params))
        
        # Stage
        list_stages = self.generate_stage(pipeline_stages, list_action)

        # Pipeline
        resources.extend(list_codebuild)
        resources.extend(self.generate_pipeline(list_stages,params['Projeto']))

        # Template
        template = self.generate_template(resources)

        # Save swap
        filename = self.save_swap(params['Projeto'], template, env)
        return filename