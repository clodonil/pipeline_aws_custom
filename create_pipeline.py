from engine.engine import Engine
import sys


playload = sys.argv[1]
pipeline = Engine()
retorno = pipeline.make_pipeline(playload)

