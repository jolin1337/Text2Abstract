import sys
import os
import traceback

if __name__ == '__main__':
    try:
        if 'serve' in sys.argv:
            #from web.serve import start_server
            #start_server()
            from web.app import app
            app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
        if 'train' in sys.argv:
            from learning import config, model
            model.train_and_store_model(config.data['articles'], config.model['categorization_model']['name'])
    except Exception as e:
        # Write out an error file. This will be returned as the failureReason in the
        # DescribeTrainingJob result.
        trc = traceback.format_exc()
        with open(os.path.join('/opt/ml/output/', 'failure'), 'w') as s:
            s.write('Exception during training: ' + str(e) + '\n' + trc)
        # Printing this causes the exception to be in the training job logs, as well.
        print('Exception during training: ' + str(e) + '\n' + trc, file=sys.stderr)
        # A non-zero exit code causes the training job to be marked as Failed.
        sys.exit(255)
