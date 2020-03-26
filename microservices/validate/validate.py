from tools.validates import Validate
from tools.callback import  CallBack
from tools.sqs import sqs_receive, sqs_send, sqs_delete
from tools.config import filas
import json

validate = Validate()

while True:
  for event in sqs_receive(filas['payload'] ):
    template = json.loads(event.body)
    result = validate.check_template(template)

    if result['status']:
        sqs_send(filas['processing'],template)
        sqs_delete(event)
    else:
        pass
        #protocol = template_yml['callback']['protocolo']
        #endpoint = template_yml['callback']['endpoint']
        #pipelineName = template_yml['callback']['pipelineName']
        #callback = CallBack(protocolo, endpoint, pipelineName)
        #callback.send(Msg)






