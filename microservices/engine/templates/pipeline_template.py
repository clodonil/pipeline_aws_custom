from troposphere import Template, Parameter, ec2, Ref
from templates.codepipeline.pipeline import NewPipeline
from templates.codebuild.newcodebuild import NewCodeBuild
from tools.config import (
    VPCID,
    PrivateSubnetOne,
    PrivateSubnetTwo,
    DevAccount,
    HomologAccount,
    ProdAccount,
    KMSKeyArn,
    TokenAqua,
    DevSecOpsAccount,
    DevToolsAccount,
)
import os


class NewTemplate:
    def __init__(self, codepipeline_role, codebuild_role, DevSecOps_Role):
        self.codepipeline_role = codepipeline_role
        self.codebuild_role = codebuild_role
        self.DevSecOps_Role = DevSecOps_Role

    def pipeline_parameter(self):

        params_vpcid = Parameter(
            "VPCID",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=VPCID
        )
        params_subnet1 = Parameter(
            "PrivateSubnetOne",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=PrivateSubnetOne
        )
        params_subnet2 = Parameter(
            "PrivateSubnetTwo",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=PrivateSubnetTwo
        )
        params_DevAccount = Parameter(
            "DevAccount",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=DevAccount
        )
        params_HomologAccount = Parameter(
            "HomologAccount",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=HomologAccount
        )
        params_ProdAccount = Parameter(
            "ProdAccount",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=ProdAccount
        )
        params_KMSKeyArn = Parameter(
            "KMSKeyArn",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=KMSKeyArn
        )
        params_TokenAqua = Parameter(
            "TokenAqua",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=TokenAqua
        )
        params_DevSecOpsAccount = Parameter(
            "DevSecOpsAccount",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=DevSecOpsAccount
        )
        params_DevToolsAccount = Parameter(
            "DevToolsAccount",
            Type="AWS::SSM::Parameter::Value<String>",
            Default=DevToolsAccount
        )

        list_params = [
            params_vpcid,
            params_subnet1,
            params_subnet2,
            params_DevAccount,
            params_HomologAccount,
            params_ProdAccount,
            params_KMSKeyArn,
            params_TokenAqua,
            params_DevSecOpsAccount,
            params_DevToolsAccount
        ]

        return list_params

    def getparams_codebuild(self, list_yaml):
        retorno = {}
        for params in list_yaml:
            if 'source' in params:
                retorno['source'] = params['source']
            elif 'runorder' in params:
                retorno['runorder'] = str(params['runorder'])
            elif 'imagecustom' in params:
                retorno['imagemcustom'] = params['imagecustom']
            elif 'environment' in params:
                env = {}
                for dic_params in params['environment']:
                    env.update(dic_params)
                retorno['env'] = env
        return retorno

    def generate_codebuild(self, runtime, pipeline_template, stages, params, env, imageCustom):
        projeto = params['Projeto']
        featurename, microservicename = projeto.split('-')
        list_codebuild = []

        buildcustom = False
        if 'BuildCustom' in params:
            if params['BuildCustom'] == 'True':
               buildcustom = True

        codebuild = NewCodeBuild(self.codebuild_role)
        cont_stage = 0
        action_custom = 1

        for t_codebuild in stages:
            stage_custom_used = False
            if isinstance(t_codebuild, str):
                t_build_template = [item for item in pipeline_template if item.split('-')[1] == t_codebuild][0]
                if t_codebuild != 'source':
                    for l_codebuild_template in pipeline_template[t_build_template]:
                        for g_codebuild in l_codebuild_template:
                            new_codebuild = eval(f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime,branchname=env, custom=buildcustom, imageCustom=imageCustom)')
                            list_codebuild.append(new_codebuild)

            elif isinstance(t_codebuild, dict):
                name_custom_stage = list(t_codebuild.keys())[0]
                custom = name_custom_stage.split('::')
                stages_temp = []

                # Customizando o action
                if custom[-1] == 'custom' and custom[0] != 'source':
                    for list_yaml in t_codebuild[name_custom_stage]:
                        temp_name = list(list_yaml.keys())[0]
                        imagemcustom = False

                        params = self.getparams_codebuild(list_yaml[temp_name])

                        configuration = {
                            temp_name: {
                                'ProjectName': temp_name,
                                'PrimarySource': params['source'],
                                'InputArtifacts': params['source'],
                                'runorder': params['runorder']
                            }}
                        stages_temp.append(configuration)
                        list_codebuild.append(codebuild.create_codebuild(temp_name, temp_name, params['env'], params['imagemcustom']))

                    # Adicionando os codebuild do padrao
                    if t_codebuild != 'source':
                        t_build_template = [item for item in pipeline_template if item.split('-')[1] == custom[0]][0]
                        for l_codebuild_template in pipeline_template[t_build_template]:
                            for g_codebuild in l_codebuild_template:
                                new_codebuild = eval(f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime,branchname=env, custom=buildcustom, imageCustom=imageCustom)')
                                list_codebuild.append(new_codebuild)
                        pipeline_template[t_build_template].extend(stages_temp)

                # Customizando o stage
                elif custom[0] == 'custom':
                    stage_custom_used = True
                    stage_name = f'{cont_stage}.{action_custom}-{custom[1]}'
                    action_custom += 1
                    pipeline_template[stage_name] = []
                    for list_yaml in t_codebuild[name_custom_stage]:
                        temp_name = list(list_yaml.keys())[0]
                        imagemcustom = False

                        params = self.getparams_codebuild(list_yaml[temp_name])

                        configuration = {
                            temp_name: {'ProjectName': temp_name, 'PrimarySource': params['source'], 'InputArtifacts': params['source'],
                                        'runorder': params['runorder']}}
                        stages_temp.append(configuration)
                        codebuildname = temp_name

                        list_codebuild.append(codebuild.create_codebuild(codebuildname, codebuildname, params['env'], params['imagemcustom']))
                    pipeline_template[stage_name].extend(stages_temp)

            if not stage_custom_used:
                cont_stage += 1

        return list_codebuild

    def generate_template(self, parameters, resources):
        template = Template()
        # paramter
        for param in parameters:
            template.add_parameter(param)

        # resources
        for resource in resources:
            template.add_resource(resource)
        return template.to_json()

    def generate_sources(self, stages, env, reponame, role, sharedlibrary_release):
        action = {}
        pipeline = NewPipeline()

        shared_configuration = {'BranchName': sharedlibrary_release, 'RepositoryName': 'pipelineaws-sharedlibrary', "PollForSourceChanges": "false"}
        action['source'] = [pipeline.create_action('SharedLibrary', "1", shared_configuration, 'Source', role)]

        for t_codebuild in stages:
            if 'source' in t_codebuild or 'source::custom' in t_codebuild:
                if t_codebuild == 'source':
                    configuration = {'RepositoryName': reponame, 'BranchName': env}
                if 'source::custom' in t_codebuild:
                    configuration = {}
                    for config in t_codebuild['source::custom']:
                        configuration.update(config)

                    if 'BranchName' not in configuration:
                        configuration.update({'BranchName': env})
                action['source'].append(
                    pipeline.create_action(configuration['RepositoryName'], "1", configuration, 'Source'))

        return action

    def create_security_groups(self, projeto, branch):

        out_all_rule = ec2.SecurityGroupRule(
            IpProtocol='TCP', FromPort=0, ToPort=65535, CidrIp='0.0.0.0/0'
        )

        sg = ec2.SecurityGroup(
            'SG',
            VpcId=Ref("VPCID"),
            GroupName=f'{projeto}-{branch}',
            GroupDescription = 'This security group is used to control access to the container',
            SecurityGroupIngress = [out_all_rule]
        )
        return [sg]


    def generate_action(self, list_codebuild, pipeline_template, reponame, env):
        pipeline = NewPipeline()
        action = {}
        projeto = reponame.replace('-','').lower()
        for code in list_codebuild:
            title = code.title.lower()
            configuration = 0
            for k in pipeline_template:
                for t in pipeline_template[k]:
                    code_template = list(t.keys())[0]
                    code_template_env = f"{code_template}{env}"
                    if code_template.lower()  == title or code_template_env.lower()  == title:
                       configuration = list(t.values())[0]


            configuration['PrimarySource'] = reponame
            if isinstance(configuration['InputArtifacts'], list):
                configuration['InputArtifacts'][0] = reponame
            else:
                if configuration['InputArtifacts'] == "REPOAPP":
                    configuration['InputArtifacts'] = reponame
            runorder = configuration.pop('runorder')
            configuration['ProjectName'] = title
            action[title] = pipeline.create_action(title, int(runorder), configuration, 'Build')
        return action

    def generate_stage(self, pipeline_stages, list_action, env):
        pipeline = NewPipeline()
        stages = []

        for t_stage in sorted(pipeline_stages):
            control_stage = t_stage.split('-')[1]
            if control_stage == 'source':
                l_stage = []
                for stg in list_action[control_stage]:
                    l_stage.append(stg)
                stages.append(pipeline.create_stage('Source', l_stage))
            else:
                l_stage = []
                for stg in pipeline_stages[t_stage]:
                    for name_stg in stg:
                        name_stg = name_stg.lower()
                        if name_stg in list_action:
                           l_stage.append(list_action[name_stg])
                        elif f'{name_stg}{env}'in list_action:
                           l_stage.append(list_action[f'{name_stg}{env}'])
                stages.append(pipeline.create_stage(control_stage, l_stage))

        return stages

    def generate_pipeline(self, list_stages, projeto):
        pipeline = NewPipeline()
        resource = pipeline.create_pipeline(projeto, self.codepipeline_role, list_stages)
        return resource

    def save_swap(self, projeto, template, env, account):
        path = 'swap'
        if not os.path.isdir(path):
            os.mkdir(path)
        if os.path.isdir(path):
            filename = f'{path}/{projeto}-{env}-{account}.json'

            with open(filename, 'w') as file:
                file.write(template)
        return filename

    def generate(self, **tparams):
        tp = tparams['tp']
        resources = []
        list_action = {}
        projeto_name = tp['params']['Projeto']
        pipeline_name = f"{projeto_name}-{tp['env']}"

        # create codebuild
        list_codebuild = self.generate_codebuild(tp['runtime'], tp['pipeline_stages'], tp['stages'], tp['params'], tp['env'], tp['imageCustom'])

        # create action
        list_action.update(self.generate_sources(tp['stages'], tp['env'], projeto_name, self.DevSecOps_Role, tp['release']))
        list_action.update(self.generate_action(list_codebuild, tp['pipeline_stages'], projeto_name, tp['env']))

        # Stage
        list_stages = self.generate_stage(tp['pipeline_stages'], list_action, tp['env'])

        # Parameter
        list_params = self.pipeline_parameter()

        # Pipeline
        resources.extend(list_codebuild)
        resources.extend(self.generate_pipeline(list_stages, pipeline_name))
        resources.extend(self.create_security_groups(projeto_name,tp['env']))

        # Template
        template = self.generate_template(list_params, resources)

        # Save swap
        filename = self.save_swap(projeto_name, template, tp['env'], tp['account'])
        return filename
