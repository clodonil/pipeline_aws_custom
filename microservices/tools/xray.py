import logging
import time

import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch
from aws_xray_sdk.core import patch_all

xray_recorder.configure(service='My application')
#xray_recorder.configure(sampling=False)
#plugins = ('ElasticBeanstalkPlugin', 'EC2Plugin')
#xray_recorder.configure(plugins=plugins)
patch_all()


patch(['boto3'])

s3_client = boto3.client('s3')

#xray_recorder.configure(sampling=False)
xray_recorder.begin_segment('Wasabi')
xray_recorder.begin_subsegment('Validate')


for x in range(100):
    @xray_recorder.capture('Validate')
    def myfunc():
        print("Rodando Func")
        logging.warning('This is a warning message')
        logging.error('This is an error message')

        time.sleep(2)


    @xray_recorder.capture('Create')
    def create():
        print("Create User")
        time.sleep(2)


    myfunc()
    create()
# xray_recorder.configure(sampling=False,context_missing='LOG_ERROR')
# segment = xray_recorder.begin_segment('Wasabi')
# subsegment = xray_recorder.begin_subsegment('Validade')
#
#
# time.sleep(1)
# print("Ola Mundo")
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# # your code here
#
# xray_recorder.begin_subsegment('Create')
# time.sleep(3)
# print("Validade")
# # some code block you want to record
xray_recorder.end_subsegment()
xray_recorder.end_segment()