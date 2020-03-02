from codepipeline.pipeline import NewPipeline
from codebuild.newcodebuild import NewCodeBuild
from templates.pipeline_template import NewTemplate
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
        make = self.load(filename)
        runtime = make['runtime']
        template = make['template']
        stages = make['pipeline']

        # Template Base
        pipeline = NewTemplate(template)
        template = pipeline.app_ecs(runtime, 'dev', stages)
        print(template)


pipeline = Engine()
retorno = pipeline.make_pipeline('/home/clodonil/Workspace/PipelineGenerate/playload.yml')

