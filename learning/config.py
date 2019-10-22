from dotenv import load_dotenv
load_dotenv()

import os
import yaml

env = os.environ.get('ENV', 'test')
_config = yaml.load(open(os.path.abspath("config/%s.yml" % (env, ))), Loader=yaml.FullLoader)
model = _config['model']
data = _config['data']

verbose = _config.get('verbose', False)

def get_full_model(param):
    return model['path'] + model[param]

def get_full_data(param):
    return data['path'] + data[param]
