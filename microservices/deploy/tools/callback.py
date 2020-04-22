"""
Tools para enviar mensagem de callBack via sns
"""

class CallBack:
    def __init__(self, protocol, endpoint, pipelineName):
        pass


    def create_sns(self):
        """
        criar o topico SNS
        """
        return True

    def inscricao(self):
        """
        inscrever o endpoint na fila SNS correta
        """

        return True


    def send(self):
        """
        enviar a mensagem para o topico
        """
        return False


