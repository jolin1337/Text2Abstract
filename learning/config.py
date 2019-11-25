from dotenv import load_dotenv
load_dotenv()

import os
import yaml

env = os.environ.get('ENV', 'test')
path = os.path.join(os.sep, os.path.dirname(os.path.realpath(__file__)), '..', "config/%s.yml")
file = open(os.path.abspath(path % (env, )))
_config = yaml.load(file, Loader=yaml.FullLoader)
file.close()
model = _config['model']
data = _config['data']

verbose = _config.get('verbose', False)

def get_full_model(param):
    return model['path'] + model[param]

def get_full_data(param):
    return data['path'] + data[param]
