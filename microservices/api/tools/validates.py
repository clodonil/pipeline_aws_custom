"""
Tools para validar o arquivo template recebido do SQS
"""
import yaml


class Validate:
    def __init__(self):
        pass

    def check_validate_yml(self, template):
        """
        valida se o arquivo yml é valido
        """
        if template:
           return True
        else:
           return False

    def check_yml_struct(self, template):
        """
        Valida se a estrutura do yml é valido
        """
        if template:
           return True
        else:
           return False

    def check_template_exist(self, template):
        """
        Valida se o template informado no arquivo yml existe
        """
        if template:
           return True
        else:
           return False

    def check_callback_protocol_endpoint(self, template):
        """
        validar se o protocolo e endpoint são validos
        """
        return True

    def check_template(self, template):
        if  self.check_validate_yml(template) \
                and self.check_yml_struct(template) \
                and self.check_template_exist(template) \
                and self.check_callback_protocol_endpoint(template):
            msg = {"status": True}
            return msg
        else:
            msg = {'status': False, 'message': 'problema no arquivo yml'}
            return msg


def change_yml_to_json(content):
    try:
        template_json = yaml.safe_load(content)
        return template_json
    except yaml.YAMLError as error:
      return  {"message": str(error)}
