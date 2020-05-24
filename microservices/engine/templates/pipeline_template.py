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
from tools.log import WasabiLog

class NewTemplate:
    def __init__(self, codepipeline_role, codebuild_role, DevSecOps_Role):
        self.codepipeline_role = codepipeline_role
        self.codebuild_role = codebuild_role
        self.DevSecOps_Role = DevSecOps_Role

    @WasabiLog
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

    @WasabiLog
    def getparams_codebuild(self, list_yaml):
        retorno = {}
        for params in list_yaml:
            if 'source' in params:
                if isinstance(params['source'], list):
                    retorno['source'] = [item.title() for item in params['source']]
                else:
                    retorno['source'] = params['source'].title()

            elif 'runorder' in params:
                retorno['runorder'] = str(params['runorder'])
            elif 'imagecustom' in params:
                retorno['imagemcustom'] = params['imagecustom']
            elif 'environment' in params:
                env = {}
                if 'environment' in params and params['environment'] != None:
                    for dic_params in params['environment']:
                        env.update(dic_params)
                retorno['env'] = env
        return retorno

    @WasabiLog
    def codebuild_mandatory(self, buildName,pipeline_template):
        """
        retorna true, se o action eh de um codebuild mandatorio
        """
        retorno = False
        for stages in pipeline_template.values():
            for action in stages:
                if buildName in action:
                    return True
        return retorno

    @WasabiLog
    def check_is_source(self, codebuild):
        check = False
        if isinstance(codebuild, str):
            if codebuild.lower() == 'source':
               check = True
        elif isinstance(codebuild, dict):
            name_custom_stage = list(codebuild.keys())[0]
            custom = name_custom_stage.split('::')
            if custom[0].lower() == 'source' and custom[1].lower() == 'custom':
               check = True
        return check

    @WasabiLog
    def generate_codebuild(self, runtime, pipeline_template, stages, params, env, imageCustom):
        projeto = params['Projeto']
        featurename, microservicename = projeto.split('-')
        list_codebuild = []
        buildcustom = False
        if 'BuildCustom' in params:
            if params['BuildCustom'] == 'True':
                buildcustom = True
        codebuild = NewCodeBuild(self.codebuild_role)
        cont_stage = 1
        action_custom = 1

        for t_codebuild in stages:
            stage_custom_used = False

            # Verifica se eh um source, se for nao faz nada
            if self.check_is_source(t_codebuild):
                continue

            # Cria os codebuild do stage sem customizacao
            elif isinstance(t_codebuild, str):
                t_build_template = [item for item in pipeline_template if item.split('-')[1] == t_codebuild][0]
                for l_codebuild_template in pipeline_template[t_build_template]:
                    for g_codebuild in l_codebuild_template:
                        new_codebuild = eval(f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime,branchname=env, custom=buildcustom, imageCustom=imageCustom)')
                        list_codebuild.append(new_codebuild)

            # Cria novos codebuild em stage padrao
            elif isinstance(t_codebuild, dict):
                name_custom_stage = list(t_codebuild.keys())[0]
                custom  = name_custom_stage.split('::')
                stages_temp = []
                # Customizando o action
                if custom[-1].lower() == 'custom':
                    for list_yaml in t_codebuild[name_custom_stage]:
                        temp_name = list(list_yaml.keys())[0]
                        imagemcustom = False
                        params = self.getparams_codebuild(list_yaml[temp_name])
                        if self.codebuild_mandatory(temp_name,pipeline_template):
                            tstage = custom[0]
                            t_build_template = [item for item in pipeline_template if item.split('-')[1] == tstage][0]
                            for l_codebuild_template in pipeline_template[t_build_template]:
                                if temp_name in l_codebuild_template:
                                    list_inputs = l_codebuild_template[temp_name]['InputArtifacts']
                                    list_inputs[list_inputs.index('App')] = params['source']
                                    l_codebuild_template[temp_name]['PrimarySource'] = params['source']
                        else:
                            if isinstance(params['source'], list):
                                primarysource = params['source'][0]
                            else:
                                primarysource = params['source']

                            configuration = {
                                temp_name: {
                                    'ProjectName': temp_name,
                                    'PrimarySource': primarysource,
                                    'InputArtifacts': params['source'],
                                    'runorder': params['runorder']
                                }}
                            stages_temp.append(configuration)
                            envs =[]
                            if 'env' in params:
                                envs.append(params.get('env'))
                            list_codebuild.append(codebuild.create_codebuild(temp_name, temp_name, envs, params.get('imagemcustom')))

                    # Adicionando os codebuild do padrao
                    tstage = custom[0]
                    t_build_template = [item for item in pipeline_template if item.split('-')[1] == tstage][0]
                    for l_codebuild_template in pipeline_template[t_build_template]:
                        for g_codebuild in l_codebuild_template:
                            new_codebuild = eval(f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime,branchname=env, custom=buildcustom, imageCustom=imageCustom)')
                            list_codebuild.append(new_codebuild)
                    pipeline_template[t_build_template].extend(stages_temp)

                # Customizando o stage
                elif custom[0].lower() == 'custom':
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
                        envs =[]
                        if 'env' in params:
                            envs.append(params.get('env'))
                        list_codebuild.append(codebuild.create_codebuild(codebuildname, codebuildname, envs, params.get('imagemcustom')))
                    pipeline_template[stage_name].extend(stages_temp)
            if not stage_custom_used:
                cont_stage += 1
        return list_codebuild

    @WasabiLog
    def generate_template(self, parameters, resources):
        template = Template()
        # paramter
        for param in parameters:
            template.add_parameter(param)
        # resources
        for resource in resources:
            template.add_resource(resource)
        return template.to_json()

    @WasabiLog
    def generate_sources(self, stages, env, reponame, role, sharedlibrary_release):
        action = {}
        pipeline = NewPipeline()
        shared_configuration = {'BranchName': sharedlibrary_release, 'RepositoryName': 'pipelineaws-sharedlibrary', "PollForSourceChanges": "false", "OutputArtifacts" : "Libs"}
        #action['Source'] = [pipeline.create_action('SharedLibrary', "1", shared_configuration, 'Source', role)]
        action['Source'] = [pipeline.create_action('SharedLibrary', "1", shared_configuration, 'Source')]
        for t_codebuild in stages:
            if 'Source' in t_codebuild or 'Source::custom' in t_codebuild:
                if t_codebuild == 'Source':
                    configuration = {'RepositoryName': reponame, 'BranchName': env, 'OutputArtifacts': 'App' }
                if 'Source::custom' in t_codebuild:
                    configuration = {}
                    for config in t_codebuild['Source::custom']:
                        configuration.update(config)
                    if 'BranchName' not in configuration:
                        configuration.update({'BranchName': env})
                action['Source'].append(
                    pipeline.create_action(configuration['RepositoryName'], "1", configuration, 'Source'))
        return action

    @WasabiLog
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

    @WasabiLog
    def generate_action(self, list_codebuild, pipeline_template, reponame, env):
        pipeline = NewPipeline()
        action = {}
        for code in list_codebuild:
            title = code.title.lower()
            configuration = 0
            for k in pipeline_template:
                for t in pipeline_template[k]:
                    code_template = list(t.keys())[0]
                    code_template_env = f"{code_template}{env}"
                    if code_template.lower()  == title or code_template_env.lower()  == title:
                        configuration = list(t.values())[0]
            runorder = configuration.pop('runorder')
            configuration['ProjectName'] = code.Name
            action[title] = pipeline.create_action(title.capitalize(), int(runorder), configuration, 'Build')
        return action

    @WasabiLog
    def check_stage_not_env(self, stage, env):
        '''
        Stages que nao devem estar na pipeline devido o ambiente
        '''
        stages_not_env = {
            'develop': ['DeployHomol', 'DeployProd'],
            'master': ['DeployDev']
        }
        if stage in stages_not_env[env]:
            return False
        return True

    @WasabiLog
    def generate_stage(self, pipeline_stages, list_action, env):
        pipeline = NewPipeline()
        stages = []
        for t_stage in sorted(pipeline_stages):
            control_stage = t_stage.split('-')[1]
            if self.check_stage_not_env(control_stage, env):
                if control_stage == 'Source':
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
                    stages.append(pipeline.create_stage(control_stage, l_stage))
        return stages

    @WasabiLog
    def generate_pipeline(self, list_stages, projeto):
        pipeline = NewPipeline()
        resource = pipeline.create_pipeline(projeto, self.codepipeline_role, list_stages)
        return resource

    @WasabiLog
    def save_swap(self, projeto, template, env, account):
        path = 'swap'
        if not os.path.isdir(path):
            os.mkdir(path)
        if os.path.isdir(path):
            filename = f'{path}/{projeto}-{env}-{account}.json'

            with open(filename, 'w') as file:
                file.write(template)
        return filename

    @WasabiLog
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
