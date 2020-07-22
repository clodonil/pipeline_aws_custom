from troposphere import Template, Parameter, ec2, Ref
from templates.codepipeline.pipeline import NewPipeline
from templates.codebuild.newcodebuild import NewCodeBuild
from templates.depends.resources import DepResource
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
from tools.log import WasabiLog, logger


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
        type_ = ' '.join([k.get('type') if k.get('type') !=
                          None else '' for k in list_yaml]).replace(' ', '')
        if type_.lower() == 'codebuild':
            for params in list_yaml:
                if 'source' in params:
                    if isinstance(params['source'], list):
                        retorno['source'] = [item.title()
                                             for item in params['source']]
                    else:
                        retorno['source'] = params['source'].title()

                elif 'runorder' in params:
                    retorno['runorder'] = str(params['runorder'])
                elif 'imagecustom' in params:
                    retorno['imagemcustom'] = params['imagecustom']
                elif 'environment' in params:
                    env = {}
                    if ('environment' in params) and (params.get('environment') is not None):
                        for dic_params in params['environment']:
                            env.update(dic_params)
                    retorno['env'] = env
        else:
            for params in list_yaml:
                retorno.update(params)
        return retorno

    def codebuild_mandatory(self, buildName, pipeline_template):
        """
        retorna true, se o action eh de um codebuild mandatorio
        """
        retorno = False
        for stages in pipeline_template.values():
            for action in stages:
                if buildName in action:
                    return True
        return retorno

    def return_type_pipeline_template(self, name, pipeline_template):
        types = 'None'
        for pipe in pipeline_template:
            for confs in pipeline_template[pipe]:
                stage_name = ''.join(confs.keys())
                if name.lower() == stage_name.lower():
                    types = ' '.join([confs[k]['type'] for k in confs])
                    break
        return types

    def check_is_not_codebuild(self, codebuild, pipeline_template):
        check = False
        if isinstance(codebuild, str):
            types = self.return_type_pipeline_template(
                codebuild, pipeline_template)
            if types.lower() != 'codebuild':
                check = True

        return check

    def check_is_not_codebuild_custom(self, name, template):
        retorno = False
        types = template[name][0]['type']
        if types.lower() != 'codebuild':
            retorno = True
        return retorno

    def check_source(self, name):

        if isinstance(name, str):
            if name.lower() == 'source':
                return True
        elif isinstance(name, dict):
            name_ = ''.join(name.keys())

            if name_.lower() == 'source::custom' or name_.lower() == 'source':
                return True

        return False

    def generate_codebuild(self, runtime, pipeline_template, stages, params, env, imageCustom):
        projeto = params['Projeto']
        featurename, microservicename = projeto.split('-')
        list_codebuild = []
        buildcustom = False
        if 'BuildCustom' in params:
            if params['BuildCustom'] == 'True':
                buildcustom = True
                logger.info(f"Build Customizado: {buildcustom}")
        codebuild = NewCodeBuild(self.codebuild_role)
        cont_stage = 1
        action_custom = 1

        for t_codebuild in stages:
            stage_custom_used = False

            if self.check_source(t_codebuild):
                continue

            # Cria os codebuild do stage sem customizacao
            elif isinstance(t_codebuild, str):
                t_build_template = [
                    item for item in pipeline_template if item.split('-')[1] == t_codebuild][0]
                for l_codebuild_template in pipeline_template[t_build_template]:
                    codebuild_name = ' '.join(l_codebuild_template.keys())
                    iscodebuild = not(self.check_is_not_codebuild(
                        codebuild_name, pipeline_template))
                    if iscodebuild:
                        for g_codebuild in l_codebuild_template:
                            new_codebuild = eval(
                                f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime, branchname=env,custom=buildcustom,imageCustom=imageCustom)')
                            list_codebuild.append(new_codebuild)

            # Cria novos codebuild em stage padrao
            elif isinstance(t_codebuild, dict):
                name_custom_stage = list(t_codebuild.keys())[0]
                custom = name_custom_stage.split('::')
                stages_temp = []

                # Customizando o action
                if custom[-1].lower() == 'custom':
                    for list_yaml in t_codebuild[name_custom_stage]:
                        temp_name = list(list_yaml.keys())[0]

                        # imagemcustom = False
                        params = self.getparams_codebuild(list_yaml[temp_name])
                        if self.codebuild_mandatory(temp_name, pipeline_template):
                            tstage = custom[0]
                            t_build_template = [
                                item for item in pipeline_template if item.split('-')[1] == tstage][0]
                            for l_codebuild_template in pipeline_template[t_build_template]:
                                if temp_name in l_codebuild_template:
                                    list_inputs = l_codebuild_template[temp_name]['InputArtifacts']
                                    list_inputs[list_inputs.index(
                                        'App')] = params['source']
                                    l_codebuild_template[temp_name]['PrimarySource'] = params['source']
                        else:
                            # Entra se for codebuild
                            if not self.check_is_not_codebuild_custom(
                                    temp_name, list_yaml):

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
                                envs = []
                                if 'env' in params:
                                    envs.append(params.get('env'))
                                list_codebuild.append(codebuild.create_codebuild(
                                    temp_name, temp_name, envs, params.get('imagemcustom')))
                    # Adicionando os codebuild do padrao
                    tstage = custom[0]
                    t_build_template = [
                        item for item in pipeline_template if item.split('-')[1] == tstage][0]
                    for l_codebuild_template in pipeline_template[t_build_template]:
                        for g_codebuild in l_codebuild_template:
                            new_codebuild = eval(
                                f'codebuild.{g_codebuild}(featurename=featurename,microservicename=microservicename,runtime=runtime,branchname=env, custom=buildcustom, imageCustom=imageCustom)')
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
                        # imagemcustom = False
                        params = self.getparams_codebuild(list_yaml[temp_name])
                        configuration = {
                            temp_name: {'ProjectName': temp_name,
                                        'PrimarySource': params['source'],
                                        'InputArtifacts': params['source'],
                                        'runorder': params['runorder']}}
                        stages_temp.append(configuration)
                        codebuildname = temp_name
                        envs = []
                        if 'env' in params:
                            envs.append(params.get('env'))
                        list_codebuild.append(codebuild.create_codebuild(
                            codebuildname, codebuildname, envs, params.get('imagemcustom')))
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
        shared_configuration = {'BranchName': sharedlibrary_release, 'RepositoryName': 'pipelineaws-sharedlibrary',
                                "PollForSourceChanges": "false", "OutputArtifacts": "Libs"}
        # action['Source'] = [pipeline.create_action(
        #    'SharedLibrary', "1", shared_configuration, 'Source', role)]
        action['Source'] = [pipeline.create_action(
            'SharedLibrary', "1", shared_configuration, 'Source')]
        for t_codebuild in stages:
            if isinstance(t_codebuild, str):
                source_ = t_codebuild
            else:
                source_ = ''.join(t_codebuild.keys())
            if 'source' == source_.lower() or 'source::custom' == source_.lower():
                if isinstance(t_codebuild, str):
                    configuration = {'RepositoryName': reponame,
                                     'BranchName': env, 'OutputArtifacts': 'App'}
                elif isinstance(t_codebuild, dict):
                    if 'source' == source_.lower():
                        branch = t_codebuild[source_][0]['BranchName']
                        configuration = {'RepositoryName': reponame,
                                         'BranchName': branch, 'OutputArtifacts': 'App'}

                    elif 'source::custom' in source_.lower():
                        configuration = {}
                        for config in t_codebuild['Source::custom']:
                            configuration.update(config)
                        if 'BranchName' not in configuration:
                            configuration.update({'BranchName': env})
                action['Source'].append(
                    pipeline.create_action(configuration['RepositoryName'], "1", configuration, 'Source'))
        return action

    def check_stage_not_env(self, estrutura, stage, env):
        '''
        Stages que nao devem estar na pipeline devido o ambiente
        '''
        if stage in estrutura[env]:
            return False
        return True

    def generate_stage(self, pipeline_stages, list_action, env, estrutura):
        pipeline = NewPipeline()
        stages = []
        for t_stage in sorted(pipeline_stages):
            control_stage = t_stage.split('-')[1]
            if self.check_stage_not_env(estrutura, control_stage, env):
                if control_stage == 'Source':
                    l_stage = []
                    for stg in list_action[control_stage]:
                        l_stage.append(stg)
                    stages.append(pipeline.create_stage('Source', l_stage))
                else:
                    l_stage = []
                    # print(pipeline_stages[t_stage])
                    for stg in pipeline_stages[t_stage]:
                        for name_stg in stg:
                            name_stg = name_stg.lower()
                            if name_stg in list_action:
                                l_stage.append(list_action[name_stg])
                    stages.append(pipeline.create_stage(
                        control_stage, l_stage))
        return stages

    def generate_pipeline(self, list_stages, projeto):
        pipeline = NewPipeline()
        resource = pipeline.create_pipeline(
            projeto, self.codepipeline_role, list_stages)
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

    def check_type_action(self, stages, pipeline_template, type):
        list_stage = {}
        for stage in stages:
            if isinstance(stage, str):
                list_stage[stage] = []
                for pipe in pipeline_template:
                    pipe_stage = pipe.split('-')[1]
                    if stage.lower() == pipe_stage.lower():
                        for confs in pipeline_template[pipe]:
                            for conf in confs:
                                if 'type' in confs[conf]:
                                    if type.lower() == confs[conf]['type'].lower():
                                        list_stage[stage].append(confs)
        return list_stage

    def generate_action(self, stages, pipeline_template, list_codebuild, env):
        types = ['InvokeLambda', 'Approval']
        template_action = {}
        pipeline = NewPipeline()

        # Buscando o invokelambda e approval no template base e criando o action
        for type_ in types:
            actions = self.check_type_action(
                stages, pipeline_template, type_)

            for key in actions:
                for action in actions[key]:
                    name = ' '.join(action.keys())
                    configuration = action[name]
                    runorder = configuration.pop('runorder')
                    configuration.pop('type')
                    template_action[name.lower()] = pipeline.create_action(
                        name.capitalize(), int(runorder), configuration, type_)

        # Criando Actions com codebuild
        for code in list_codebuild:
            title = code.title.lower()
            configuration = 0
            for k in pipeline_template:
                for t in pipeline_template[k]:
                    code_template = list(t.keys())[0]
                    code_template_env = f"{code_template}{env}"
                    if (code_template.lower() == title) or (code_template_env.lower() == title):
                        configuration = list(t.values())[0]
            runorder = configuration.pop('runorder')
            if 'type' in configuration:
                configuration.pop('type')
            configuration['ProjectName'] = code.Name
            template_action[title] = pipeline.create_action(
                title.capitalize(), int(runorder), configuration, 'CodeBuild')

        # Action custom
        for action in stages:
            if isinstance(action, dict):
                index_action = ' '.join(action.keys())
                custom = index_action.split('::')
                if custom[-1].lower() == 'custom' and custom[0].lower() != 'source':
                    # print(stage[index_stage])

                    for confs in action[index_action]:
                        name = ' '.join(confs.keys())
                        params = self.getparams_codebuild(
                            confs[name])
                        type_ = params.get('type')
                        if type_ != None:
                            configuration = params
                            runorder = params.pop('runorder')
                            params.pop('type')
                            template_action[name.lower()] = pipeline.create_action(
                                name.capitalize(), int(runorder), configuration, type_)

                            tstage = custom[0]
                            t_build_template = [
                                item for item in pipeline_template if item.split('-')[1] == tstage][0]
                            action_custom = [{name: {'ProjectName': name}}]
                            pipeline_template[t_build_template].extend(
                                action_custom)
        return template_action

    def create_depends(self, projeto_name, env, deps):
        logger.info(f"Criando dependencias")
        resource = DepResource()
        list_resource = []
        for dep in deps[env]:
            name = f"{projeto_name}-{dep}"
            list_resource.append(eval(f'resource.{dep}(name)'))

        return list_resource

    def generate(self, **tparams):
        tp = tparams['tp']
        resources = []
        list_action = {}
        projeto_name = tp['params']['Projeto']
        pipeline_name = f"{projeto_name}-{tp['env']}"
        logger.info(f"Generate Template {pipeline_name}")

        # create codebuild
        list_codebuild = self.generate_codebuild(
            tp['runtime'], tp['pipeline_stages'], tp['stages'], tp['params'], tp['env'], tp['imageCustom'])

        # create action
        list_action.update(self.generate_sources(
            tp['stages'], tp['env'], projeto_name, self.DevSecOps_Role, tp['release']))
        list_action.update(self.generate_action(
            tp['stages'], tp['pipeline_stages'], list_codebuild, tp['env']))

        # Stage
        list_stages = self.generate_stage(
            tp['pipeline_stages'], list_action, tp['env'], tp['structure'])

        # Parameter
        list_params = self.pipeline_parameter()

        # Pipeline
        resources.extend(list_codebuild)
        resources.extend(self.generate_pipeline(list_stages, pipeline_name))
        resources.extend(self.create_depends(
            projeto_name, tp['env'], tp['depends']))

        # Template
        template = self.generate_template(list_params, resources)

        # Save swap
        filename = self.save_swap(
            projeto_name, template, tp['env'], tp['account'])
        return filename
