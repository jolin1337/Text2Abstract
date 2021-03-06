# Build an image that can do training and inference in SageMaker
# This is a Python 2 image that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.

FROM ubuntu:16.04

MAINTAINER Amazon AI <sage-learner@amazon.com>


WORKDIR /opt
COPY requirements.txt /opt/requirements.txt

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python3 \
         nginx \
         python-gevent python-gevent-websocket \
         git \
         libicu-dev \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN alias python=python3

# Here we get all python packages.
# There's substantial overlap between scipy and numpy that we eliminate by
# linking them together. Likewise, pip leaves the install caches populated which uses
# a significant amount of space. These optimizations save a fair amount of space in the
# image, which reduces start up time.
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && \
    pip install -r requirements.txt && \
        rm -rf /root/.cache

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV MODEL_PATH=/opt/ml/model
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"
ENV ENV=sagemaker
RUN rm requirements.txt get-pip.py

# Set up the program in the image
COPY web /opt/program/web
COPY learning /opt/program/learning
COPY config /opt/program/config
COPY _sagemaker/sagemaker.py /opt/program/sagemaker.py

WORKDIR /opt/program


ENTRYPOINT ["python3", "sagemaker.py"]
