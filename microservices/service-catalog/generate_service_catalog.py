import yaml
filename = '../../exemplos/payload_error.yml'

def change_yml_to_json(ftemplate):
    try:
      with open(ftemplate, 'r') as stream:
        template_json = (yaml.safe_load(stream))
        return template_json
    except yaml.YAMLError as error:
      return  {"message": str(error)}


retorno = change_yml_to_json(filename)
print(retorno)