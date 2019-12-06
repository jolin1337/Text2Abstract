import datetime
import boto3
import json
import os

# Prefix to give to training jobs, models, and endpoint configs, and endpoint name
MODEL_PREFIX = os.environ['MODEL_PREFIX'] 

# Name of Parameter Store key corresponding to value of last successful training job date
LAST_TRAIN_PARAM = '/models/{}/train/latest'.format(MODEL_PREFIX) 

# Name of bucket containing training data and to output model artifacts to
BUCKET = os.environ['BUCKET'] # Name of bucket

# Prefix of training data files in bucket
TRAIN_SET_PREFIX = os.path.join('data', MODEL_PREFIX, 'train')

# Path to location of training data files
TRAIN_SET_PATH = os.path.join('s3://', BUCKET, TRAIN_SET_PREFIX, '')


# Path to output model artifacts to
OUTPUT_PATH = os.path.join('s3://', BUCKET, 'models', MODEL_PREFIX, '')

s3 = boto3.client('s3')
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    time = event['time']
    if not check_objects_exists():
        return {
            'no_new_data': True
        }

    return {
        'time': time,
        'train_set_uri': TRAIN_SET_PATH,
        's3_output_path': OUTPUT_PATH,
        'last_train_param': LAST_TRAIN_PARAM,
        'endpoint': MODEL_PREFIX,
        'no_new_data': False
    }

def check_objects_exists():
    """ Checks to see if the input filenames exist as objects in S3
    Returns:
        (list)
        Filtered list containing string paths of filenames that exist as objects in S3
        Or False if no files found
    """
    objects = s3.list_objects(Bucket=BUCKET, Prefix=TRAIN_SET_PATH)
    if objects:
        return objects
    return False
