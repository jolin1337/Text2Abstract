# Text2Abstract
#
# VERSION               0.0.2

FROM java:8
MAINTAINER Johannes Lindén <johannes@godesity.se>

ENV SYNTAXNETDIR=/opt/tensorflow PATH=$PATH:/root/bin

RUN mkdir -p $SYNTAXNETDIR \
    && cd $SYNTAXNETDIR \
    && apt-get update \
    && apt-get install git zlib1g-dev file swig python2.7 python-dev python-pip -y \
    && pip install --upgrade pip \
    && pip install -U protobuf==3.0.0b2 \
    && pip install asciitree numpy python-env gensim \
    && pip install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0rc0-cp27-none-linux_x86_64.whl \
    && wget https://github.com/bazelbuild/bazel/releases/download/0.2.2b/bazel-0.2.2b-installer-linux-x86_64.sh \
    && chmod +x bazel-0.2.2b-installer-linux-x86_64.sh \
    && ./bazel-0.2.2b-installer-linux-x86_64.sh --user \
    && git clone --recursive https://github.com/tensorflow/models.git
RUN cd $SYNTAXNETDIR/models \
    && git pull \
    && cd $SYNTAXNETDIR/models/syntaxnet/tensorflow \
    && echo "\n\n\n" | ./configure \
    && apt-get autoremove -y \
    && apt-get clean

RUN cd $SYNTAXNETDIR/models/syntaxnet \
    && bazel test syntaxnet/... util/utf8/...

WORKDIR $SYNTAXNETDIR/models/syntaxnet

#CMD [ "sh", "-c", "echo 'Bob brought the pizza to Alice.' | syntaxnet/demo.sh" ]

RUN mkdir swe_model \
	&& cd swe_model \
	&& wget http://download.tensorflow.org/models/parsey_universal/Swedish.zip \
	&& unzip Swedish.zip \
	&& cd ..

CMD /root/models/syntaxnet/models/parsey_universal/parse.sh $SYNTAXNETDIR/models/syntaxnet/swe_model
