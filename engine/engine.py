from codepipeline.pipeline import NewPipeline
from codebuild.newcodebuild import NewCodeBuild
from templates.pipeline_template import NewTemplate
from tools.s3 import upload_file_s3
from tools.cloudformation import deploy

import yaml

class Engine:
    def load(self, filename):
        with open(filename, 'r') as stream:
          try:
             pipeline_template = (yaml.safe_load(stream))
          except yaml.YAMLError as exc:
            raise(exc)
        
        return pipeline_template

    def make_pipeline(self,filename):
        params = {}
        make = self.load(filename)
        runtime = make['runtime']
        template = make['template']
        stages = make['pipeline']

        for param in make['Parameter']:
            params.update(param)

        # Template Base
        pipeline = NewTemplate(template)
        file_template = pipeline.generate(runtime, 'dev', stages, template, params)
        path = upload_file_s3(file_template)

        # Deploy
        deploy(params['Projeto'], file_template)
        


pipeline = Engine()
retorno = pipeline.make_pipeline('/home/clodonil/Workspace/pipeline_aws_custom/playload_custom1.yml')

