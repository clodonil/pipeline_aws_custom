from functools import wraps
import logging
import logging.config
import os


typelog = os.environ.get('LOG')
if typelog != 'prod':
   typelog = 'root'

path='logs'
if not os.path.isdir(path):
    os.mkdir(path)

logging.config.fileConfig('tools/wasabi_log.ini')
logger = logging.getLogger(typelog)

def WasabiLog(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        l_string = f'func:{func.__name__}:args:{args}:kwargs:{kwargs}:result:{result}'
        logger.debug(l_string)
        return result
    return inner
