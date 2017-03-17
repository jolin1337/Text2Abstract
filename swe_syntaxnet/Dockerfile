# Text2Abstract
#
# VERSION               0.0.2

FROM java:8
MAINTAINER Johannes Lindén <johannes@godesity.se>

ENV SYNTAXNETDIR=/opt/tensorflow PATH=$PATH:/root/bin
ENV TEXT2ABSTRACT_DIR=/opt/Text2Abstract

RUN mkdir -p $SYNTAXNETDIR && mkdir -p TEXT2ABSTRACT_DIR
WORKDIR $TEXT2ABSTRACT_DIR

# Update and install dependencies
RUN apt-get update \
    && apt-get install git zlib1g-dev file swig python2.7 python-dev python-pip -y \
    && apt-get install nodejs-legacy npm -y

#install node
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.11.1/install.sh | bash \
	&& . ~/.profile \
	&& nvm install 4.0.0 \
	&& nvm use 4.0.0 \
	&& nvm alias default 4.0.0 \
	&& npm install express body-parser async \
	&& npm install -g vue-cli  \
	&& npm install -g babel-preset-es2015


# Upgrading pip
RUN pip install --upgrade pip \
    && pip install -U protobuf==3.0.0b2
# Install math dependencies in python pip
RUN pip install --user asciitree \
    && pip install --user numpy scipy sklearn \
    && pip install  --user python-env gensim \
	&& pip install tensorflow
RUN apt-get install python-psycopg2

EXPOSE 3000
EXPOSE 8080

# WORKDIR $SYNTAXNETDIR
# RUN pip install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0rc0-cp27-none-linux_x86_64.whl
#     && wget https://github.com/bazelbuild/bazel/releases/download/0.3.1/bazel-0.3.1-installer-linux-x86_64.sh \
#     && chmod +x bazel-0.3.1-installer-linux-x86_64.sh \
#     && ./bazel-0.3.1-installer-linux-x86_64.sh --user \
#     && git clone --recursive https://github.com/tensorflow/models.git \
#     && cd $SYNTAXNETDIR/models/syntaxnet/tensorflow \
#     && echo "\n\n\n\n" | ./configure \
#     && apt-get autoremove -y \
#     && apt-get clean

# RUN cd $SYNTAXNETDIR/models/syntaxnet \
#     && bazel test syntaxnet/... util/utf8/...

# WORKDIR $SYNTAXNETDIR/models/syntaxnet

#CMD [ "sh", "-c", "echo 'Bob brought the pizza to Alice.' | syntaxnet/demo.sh" ]

# RUN mkdir swe_model \
# 	&& cd swe_model \
# 	&& wget http://download.tensorflow.org/models/parsey_universal/Swedish.zip \
# 	&& unzip Swedish.zip \
# 	&& cd ..
RUN echo 'export NVM_DIR="/root/.nvm"' >> ~/.bashrc
RUN echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm' >> ~/.bashrc
# CMD /root/models/syntaxnet/models/parsey_universal/parse.sh $SYNTAXNETDIR/models/syntaxnet/swe_model
CMD bash
# To build
# > docker build -t text2abstract:v1.0.0 .
# To run
# > docker run -p from-port:to-port -v c:/Users/desktop-godesity/Documents/Text2Abstract/:/opt/Text2Abstract -ti text2abstract:v1.0.0 bash
#
# To stop all containers from running (do before remove all containers)
# docker stop $(docker ps -a -q)
# To remove all containers
# docker rm $(docker ps -a -q)