import boto3
import os

# AWS provided containers for the Linear Learner model
CONTAINERS = {'eu-west-1': '682250509414.dkr.ecr.eu-west-1.amazonaws.com/autocategorization:latest'}
              
REGION = boto3.session.Session().region_name

# Number of features in data
FEATURE_DIM = os.environ['FEATURE_DIM']

# Instance type to train on
TRAINING_INSTANCE_TYPE = os.environ['TRAINING_INSTANCE_TYPE']

# Role to pass to SageMaker training job that has access to training data in S3, etc
SAGEMAKER_ROLE = os.environ['SAGEMAKER_ROLE']

sagemaker = boto3.client('sagemaker')


def lambda_handler(event, context):
    time = event['time']
    model_prefix = event['endpoint']
    train_set_uri = event['train_set_uri']
    container = CONTAINERS[REGION]
    s3_output_path = event['s3_output_path']
    name = '{}-{}'.format(model_prefix, time).replace(':', '-')
    print('Starting training job...')
    create_training_job(name, train_set_uri, container, s3_output_path)
    event['name'] = name
    event['container'] = container
    event['stage'] = 'Training'
    event['status'] = 'InProgress'
    event['message'] = 'Starting training job "{}"'.format(name)
    return event


def create_training_job(name, train_set_uri, container, s3_output_path):
    """ Start SageMaker training job
    Args:
        name (string): Name to label training job with
        train_set_uri (string): URI to training data files in S3
        container (string): Registry path of the Docker image that contains the training algorithm
        s3_output_path (string): Path of where in S3 bucket to output model artifacts after training
    Returns:
        (None)
    """
    try:
        response = sagemaker.create_training_job(
            TrainingJobName=name,
            HyperParameters={
                'feature_dim': FEATURE_DIM,
                'predictor_type': 'regressor',
                'mini_batch_size': '100'
            },
            AlgorithmSpecification={
                'TrainingImage': container,
                'TrainingInputMode': 'File'
            },
            RoleArn=SAGEMAKER_ROLE,
            InputDataConfig=[
                {
                    'ChannelName': 'train',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': train_set_uri,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    },
                    'CompressionType': 'None'
                }
            ],
            OutputDataConfig={
                'S3OutputPath': s3_output_path
            },
            ResourceConfig={
                'InstanceType': TRAINING_INSTANCE_TYPE,
                'InstanceCount': 1,
                'VolumeSizeInGB': 50
            },
            StoppingCondition={
                'MaxRuntimeInSeconds': 86400
            }
        )
    except Exception as e:
        print(e)
        print('Unable to create training job.')
        raise(e)
        