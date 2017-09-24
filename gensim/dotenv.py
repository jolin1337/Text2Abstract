import os

def load(file='.env'):
    with open(file) as f:
        for line in f:
            line = line.strip()
            if '=' not in line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line.replace('export ', '', 1)
            # Remove leading `export `
            # then, split name / value pair
            key, value = line.split('=', 1)
            os.environ[key] = value

def get(envKey, otherWise=''):
    if envKey in os.environ:
        return os.environ[envKey]
    else:
        return otherWise