FROM tensorflow/tensorflow:latest-py3-jupyter
COPY requirements.txt /
RUN pip install -r /requirements.txt
