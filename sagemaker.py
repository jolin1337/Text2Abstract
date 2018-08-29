import sys

if __name__ == '__main__':
    if 'serve' in sys.argv:
        from web.app import app
        app.start()
    if 'train' in sys.argv:
        import learning.model as model
        model.train_and_store(input_file, output)
