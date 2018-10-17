import os
import yaml

env = os.environ.get('ENV', 'test')
config = yaml.load(open("config/%s.yml" % (env, )))
model = config['model']
data = config['data']

verbose = config.get('verbose', False)

def get_full_model(param):
    return model['path'] + model[param]

def get_full_data(param):
    return data['path'] + data[param]
